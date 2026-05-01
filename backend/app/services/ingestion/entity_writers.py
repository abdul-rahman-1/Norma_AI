"""
entity_writers.py
-----------------
Safe upsert writers for all 9 supported entity types.
Handles reference resolution (e.g. phone -> ObjectId) and context injection.
"""

from bson import ObjectId
from datetime import datetime
import uuid
import logging
from typing import Optional, Literal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WriteResult:
    row: int
    action: Literal["inserted", "updated", "skipped", "error"]
    id: Optional[str] = None
    reason: Optional[str] = None

async def _get_patient_id_by_phone(phone: str, db) -> Optional[ObjectId]:
    if not phone: return None
    clean = str(phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean.startswith("+") and len(clean) == 10:
        clean = f"+91{clean}"
    patient = await db.patients.find_one({"phone_number": clean})
    return patient["_id"] if patient else None

async def _get_doctor_id_by_phone(phone: str, db) -> Optional[ObjectId]:
    if not phone: return None
    clean = str(phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean.startswith("+") and len(clean) == 10:
        clean = f"+91{clean}"
    doctor = await db.doctors.find_one({"whatsapp_number": clean})
    return doctor["_id"] if doctor else None

async def write_patient(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        phone = record.get("phone_number") or record.get("phone")
        clean_phone = str(phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean_phone.startswith("+") and len(clean_phone) == 10:
            clean_phone = f"+91{clean_phone}"
        
        existing = await db.patients.find_one({"phone_number": clean_phone})
        
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate phone number")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.patients.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))
        
        new_record = record.copy()
        if not new_record.get("patient_uuid"):
            new_record["patient_uuid"] = str(uuid.uuid4())
        new_record["phone_number"] = clean_phone
        new_record["created_at"] = new_record["updated_at"] = datetime.utcnow()
        new_record["created_by"] = ObjectId(uploader_context.get("_id")) if uploader_context.get("_id") else None
        new_record["is_active"] = True
        
        result = await db.patients.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_doctor(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        phone = record.get("whatsapp_number")
        clean_phone = str(phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean_phone.startswith("+") and len(clean_phone) == 10:
            clean_phone = f"+91{clean_phone}"

        existing = await db.doctors.find_one({"whatsapp_number": clean_phone})
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate WhatsApp number")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.doctors.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))
        
        new_record = record.copy()
        if not new_record.get("doctor_uuid"):
            new_record["doctor_uuid"] = str(uuid.uuid4())
        new_record["whatsapp_number"] = clean_phone
        new_record["created_at"] = new_record["updated_at"] = datetime.utcnow()
        new_record["is_active"] = True
        
        result = await db.doctors.insert_one(new_record)
        
        login_entry = {
            "identifier": clean_phone,
            "phone_number": clean_phone,
            "username": new_record.get("email"),
            "name": new_record.get("full_name"),
            "role": "doctor",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.login_details.insert_one(login_entry)
        
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_staff(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        phone = record.get("phone_number") or record.get("phone")
        clean_phone = str(phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not clean_phone.startswith("+") and len(clean_phone) == 10:
            clean_phone = f"+91{clean_phone}"

        existing = await db.staff_users.find_one({"phone_number": clean_phone})
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate phone number")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.staff_users.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))

        new_record = record.copy()
        new_record["phone_number"] = clean_phone
        new_record["created_at"] = new_record["updated_at"] = datetime.utcnow()
        new_record["is_active"] = True
        
        if not new_record.get("doctor_id"):
             if uploader_context.get("role") == "doctor":
                 new_record["doctor_id"] = str(uploader_context["_id"])
             else:
                 return WriteResult(row, "error", reason="Missing doctor_id for staff member")
        
        result = await db.staff_users.insert_one(new_record)
        
        login_entry = {
            "identifier": clean_phone,
            "phone_number": clean_phone,
            "username": new_record.get("email"),
            "name": new_record.get("full_name"),
            "role": "staff",
            "assigned_doctor_id": str(new_record["doctor_id"]),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.login_details.insert_one(login_entry)
        
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_appointment(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        patient_id = await _get_patient_id_by_phone(record.get("patient_phone"), db)
        if not patient_id: return WriteResult(row, "error", reason="Patient not found by phone")
        
        doctor_id = await _get_doctor_id_by_phone(record.get("doctor_phone"), db)
        if not doctor_id:
             if uploader_context.get("role") == "doctor":
                 doctor_id = ObjectId(uploader_context["_id"])
             else:
                 return WriteResult(row, "error", reason="Doctor not found by phone")
        
        apt_dt = record.get("appointment_datetime") or record.get("scheduled_at")
        if not isinstance(apt_dt, datetime):
            apt_dt = datetime.fromisoformat(str(apt_dt))
            
        existing = await db.appointments.find_one({
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_datetime": apt_dt
        })
        
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate appointment")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data.pop("patient_id", None)
            update_data.pop("doctor_id", None)
            update_data.pop("appointment_datetime", None)
            update_data["updated_at"] = datetime.utcnow()
            await db.appointments.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))
            
        new_record = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_datetime": apt_dt,
            "status": record.get("status", "booked"),
            "reason": record.get("reason"),
            "notes": record.get("notes"),
            "source": record.get("source", "bulk_upload"),
            "created_by": ObjectId(uploader_context["_id"]) if uploader_context.get("_id") else None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.appointments.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_prescription(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        patient_id = await _get_patient_id_by_phone(record.get("patient_phone"), db)
        if not patient_id: return WriteResult(row, "error", reason="Patient not found by phone")
        
        doctor_id = await _get_doctor_id_by_phone(record.get("doctor_phone"), db)
        if not doctor_id:
             if uploader_context.get("role") == "doctor":
                 doctor_id = ObjectId(uploader_context["_id"])
             else:
                 return WriteResult(row, "error", reason="Doctor not found by phone")
        
        med_name = record.get("medication_name") or record.get("medication")
        start_date = record.get("start_date") or datetime.utcnow()
        if not isinstance(start_date, datetime):
            start_date = datetime.fromisoformat(str(start_date))

        existing = await db.prescriptions.find_one({
            "patient_id": patient_id,
            "medication_name": med_name,
            "start_date": start_date
        })

        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate prescription")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.prescriptions.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))

        new_record = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "medication_name": med_name,
            "dosage": record.get("dosage"),
            "frequency": record.get("frequency"),
            "start_date": start_date,
            "end_date": record.get("end_date"),
            "instructions": record.get("instructions") or record.get("notes"),
            "status": record.get("status", "active"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.prescriptions.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_medical_record(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        patient_id = await _get_patient_id_by_phone(record.get("patient_phone"), db)
        if not patient_id: return WriteResult(row, "error", reason="Patient not found by phone")
        
        doctor_id = await _get_doctor_id_by_phone(record.get("doctor_phone"), db)
        if not doctor_id:
             if uploader_context.get("role") == "doctor":
                 doctor_id = ObjectId(uploader_context["_id"])
             else:
                 return WriteResult(row, "error", reason="Doctor not found by phone")
        
        vdate = record.get("visit_date") or datetime.utcnow()
        if not isinstance(vdate, datetime):
            vdate = datetime.fromisoformat(str(vdate))
            
        existing = await db.medical_records.find_one({
            "patient_id": patient_id,
            "record_type": record.get("record_type"),
            "visit_date": vdate
        })

        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate medical record")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.medical_records.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))

        new_record = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "visit_date": vdate,
            "record_type": record.get("record_type", "consultation"),
            "symptoms": record.get("symptoms"),
            "diagnosis": record.get("diagnosis"),
            "treatment_plan": record.get("treatment_plan") or record.get("treatment"),
            "notes": record.get("notes"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.medical_records.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_clinic_info(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        key = record.get("key")
        existing = await db.clinic_info.find_one({"key": key})
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate key")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.clinic_info.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))
            
        new_record = record.copy()
        new_record["created_at"] = new_record["updated_at"] = datetime.utcnow()
        result = await db.clinic_info.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_operating_hours(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        doctor_id = await _get_doctor_id_by_phone(record.get("doctor_phone"), db)
        if not doctor_id and uploader_context.get("role") == "doctor":
             doctor_id = ObjectId(uploader_context["_id"])
        
        day = int(record.get("day_of_week"))
        existing = await db.operating_hours.find_one({"doctor_id": doctor_id, "day_of_week": day})
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate day of week for doctor")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.operating_hours.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))

        new_record = record.copy()
        new_record["doctor_id"] = doctor_id
        new_record["day_of_week"] = day
        new_record["created_at"] = new_record["updated_at"] = datetime.utcnow()
        result = await db.operating_hours.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

async def write_insurance_claim(record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    try:
        patient_id = await _get_patient_id_by_phone(record.get("patient_phone"), db)
        if not patient_id: return WriteResult(row, "error", reason="Patient not found by phone")
        
        claim_no = record.get("claim_number")
        existing = await db.insurance_claims.find_one({"claim_number": claim_no})
        if existing:
            if not overwrite:
                return WriteResult(row, "skipped", str(existing["_id"]), "Duplicate claim number")
            update_data = {k: v for k, v in record.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            await db.insurance_claims.update_one({"_id": existing["_id"]}, {"$set": update_data})
            return WriteResult(row, "updated", str(existing["_id"]))

        new_record = record.copy()
        new_record["patient_id"] = patient_id
        new_record["created_at"] = new_record["updated_at"] = datetime.utcnow()
        result = await db.insurance_claims.insert_one(new_record)
        return WriteResult(row, "inserted", str(result.inserted_id))
    except Exception as e:
        return WriteResult(row, "error", reason=str(e))

ENTITY_WRITERS = {
    "patients": write_patient,
    "doctors": write_doctor,
    "staff_users": write_staff,
    "appointments": write_appointment,
    "prescriptions": write_prescription,
    "medical_records": write_medical_record,
    "clinic_info": write_clinic_info,
    "operating_hours": write_operating_hours,
    "insurance_claims": write_insurance_claim,
}

async def write_record(entity_type: str, record: dict, row: int, db, uploader_context: dict, overwrite: bool = False) -> WriteResult:
    writer = ENTITY_WRITERS.get(entity_type)
    if not writer:
        return WriteResult(row, "error", reason=f"No writer for entity type {entity_type}")
    return await writer(record, row, db, uploader_context, overwrite)
