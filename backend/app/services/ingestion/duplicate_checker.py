"""
duplicate_checker.py — Checks each ingestion row against the DB using the
correct unique key(s) for each entity type.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DuplicateResult:
    is_duplicate: bool
    existing_id:  Optional[str]
    action:       str   # "insert" | "update"
    matched_key:  Optional[str]


def _normalise_phone(val) -> Optional[str]:
    if not val:
        return None
    clean = str(val).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean.startswith("+") and len(clean) == 10:
        clean = f"+91{clean}"
    return clean


async def _check_patients(record, db) -> DuplicateResult:
    if record.get("patient_uuid"):
        ex = await db.patients.find_one({"patient_uuid": record["patient_uuid"]})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "patient_uuid")
    phone = _normalise_phone(record.get("phone_number") or record.get("phone"))
    if phone:
        ex = await db.patients.find_one({"phone_number": phone})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "phone_number")
    if record.get("email"):
        ex = await db.patients.find_one({"email": record["email"].lower().strip()})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "email")
    return DuplicateResult(False, None, "insert", None)


async def _check_doctors(record, db) -> DuplicateResult:
    if record.get("doctor_uuid"):
        ex = await db.doctors.find_one({"doctor_uuid": record["doctor_uuid"]})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "doctor_uuid")
    phone = _normalise_phone(record.get("whatsapp_number"))
    if phone:
        ex = await db.doctors.find_one({"whatsapp_number": phone})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "whatsapp_number")
    if record.get("email"):
        ex = await db.doctors.find_one({"email": record["email"].lower().strip()})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "email")
    return DuplicateResult(False, None, "insert", None)


async def _check_staff(record, db) -> DuplicateResult:
    phone = _normalise_phone(record.get("phone_number") or record.get("phone"))
    if phone:
        ex = await db.staff_users.find_one({"phone_number": phone})
        if ex:
            return DuplicateResult(True, str(ex["_id"]), "update", "phone_number")
    return DuplicateResult(False, None, "insert", None)


async def _check_appointments(record, db) -> DuplicateResult:
    patient_phone = _normalise_phone(record.get("patient_phone"))
    doctor_phone  = _normalise_phone(record.get("doctor_phone"))
    apt_dt = record.get("appointment_datetime") or record.get("scheduled_at")
    if not (patient_phone and doctor_phone and apt_dt):
        return DuplicateResult(False, None, "insert", None)
    patient = await db.patients.find_one({"phone_number": patient_phone})
    doctor  = await db.doctors.find_one({"whatsapp_number": doctor_phone})
    if not patient or not doctor:
        return DuplicateResult(False, None, "insert", None)
    try:
        if not isinstance(apt_dt, datetime):
            apt_dt = datetime.fromisoformat(str(apt_dt))
    except Exception:
        return DuplicateResult(False, None, "insert", None)
    ex = await db.appointments.find_one({
        "patient_id": patient["_id"], "doctor_id": doctor["_id"],
        "appointment_datetime": apt_dt
    })
    if ex:
        return DuplicateResult(True, str(ex["_id"]), "update", "patient+doctor+datetime")
    return DuplicateResult(False, None, "insert", None)


async def _check_prescriptions(record, db) -> DuplicateResult:
    phone = _normalise_phone(record.get("patient_phone"))
    med   = record.get("medication_name") or record.get("medication")
    if not (phone and med):
        return DuplicateResult(False, None, "insert", None)
    patient = await db.patients.find_one({"phone_number": phone})
    if not patient:
        return DuplicateResult(False, None, "insert", None)
    query = {"patient_id": patient["_id"], "medication_name": str(med).strip()}
    if record.get("start_date"):
        query["start_date"] = record["start_date"]
    ex = await db.prescriptions.find_one(query)
    if ex:
        return DuplicateResult(True, str(ex["_id"]), "update", "patient+medication+start_date")
    return DuplicateResult(False, None, "insert", None)


async def _check_medical_records(record, db) -> DuplicateResult:
    phone = _normalise_phone(record.get("patient_phone"))
    rtype = record.get("record_type")
    if not (phone and rtype):
        return DuplicateResult(False, None, "insert", None)
    patient = await db.patients.find_one({"phone_number": phone})
    if not patient:
        return DuplicateResult(False, None, "insert", None)
    query = {"patient_id": patient["_id"], "record_type": str(rtype).strip()}
    if record.get("visit_date"):
        query["visit_date"] = record["visit_date"]
    ex = await db.medical_records.find_one(query)
    if ex:
        return DuplicateResult(True, str(ex["_id"]), "update", "patient+record_type+visit_date")
    return DuplicateResult(False, None, "insert", None)


async def _check_clinic_info(record, db) -> DuplicateResult:
    key = record.get("key")
    if not key:
        return DuplicateResult(False, None, "insert", None)
    ex = await db.clinic_info.find_one({"key": str(key).strip()})
    if ex:
        return DuplicateResult(True, str(ex["_id"]), "update", "key")
    return DuplicateResult(False, None, "insert", None)


async def _check_operating_hours(record, db) -> DuplicateResult:
    day = record.get("day_of_week")
    if day is None:
        return DuplicateResult(False, None, "insert", None)
    doctor_phone = _normalise_phone(record.get("doctor_phone"))
    doctor_id = None
    if doctor_phone:
        doc = await db.doctors.find_one({"whatsapp_number": doctor_phone})
        if doc:
            doctor_id = doc["_id"]
    query = {"day_of_week": int(day), "doctor_id": doctor_id}
    ex = await db.operating_hours.find_one(query)
    if ex:
        return DuplicateResult(True, str(ex["_id"]), "update", "doctor+day_of_week")
    return DuplicateResult(False, None, "insert", None)


async def _check_insurance_claims(record, db) -> DuplicateResult:
    cn = record.get("claim_number")
    if not cn:
        return DuplicateResult(False, None, "insert", None)
    ex = await db.insurance_claims.find_one({"claim_number": str(cn).strip()})
    if ex:
        return DuplicateResult(True, str(ex["_id"]), "update", "claim_number")
    return DuplicateResult(False, None, "insert", None)


_CHECKERS = {
    "patients":         _check_patients,
    "doctors":          _check_doctors,
    "staff_users":      _check_staff,
    "appointments":     _check_appointments,
    "prescriptions":    _check_prescriptions,
    "medical_records":  _check_medical_records,
    "clinic_info":      _check_clinic_info,
    "operating_hours":  _check_operating_hours,
    "insurance_claims": _check_insurance_claims,
}


async def check_duplicate(entity_type: str, record: dict, db) -> DuplicateResult:
    """Check if a record already exists using entity-specific unique keys."""
    checker = _CHECKERS.get(entity_type)
    if not checker:
        return DuplicateResult(False, None, "insert", None)
    try:
        return await checker(record, db)
    except Exception as e:
        logger.error(f"Duplicate check error for '{entity_type}': {e}")
        return DuplicateResult(False, None, "insert", None)
