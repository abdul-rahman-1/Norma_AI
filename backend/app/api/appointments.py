from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.db.mongodb import get_db
from app.core.security import get_current_user, require_role
from app.core.permissions import ResourceType, ActionType, check_resource_access, UserRole
from app.schemas.models import Appointment
from app.services.whatsapp_service import whatsapp_service
from app.services.notification_service import notification_service
from app.utils.slot_resolver import is_slot_available, get_available_slots, check_double_booking
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.get("", response_model=List[dict])
async def get_appointments(current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """
    Get appointments based on user role.
    
    - Admin: sees all appointments
    - Doctor: sees own appointments
    - Staff: sees assigned doctor's appointments
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    # Permission check
    user_role_enum = UserRole(user_role)
    check_resource_access(user_role_enum, ResourceType.APPOINTMENT, ActionType.LIST, current_user)
    
    match_stage = {}
    
    if user_role == "doctor":
        # Doctors see their own appointments
        doctor_id = current_user.get("_id")
        if doctor_id:
            match_stage = {"doctor_id": ObjectId(doctor_id)}
            
    elif user_role == "staff":
        # Staff see appointments of their assigned doctor
        assigned_doctor_id = current_user.get("assigned_doctor_id")
        if assigned_doctor_id:
            match_stage = {"doctor_id": ObjectId(assigned_doctor_id)}
        else:
            return []

    pipeline = [
        {
            "$lookup": {
                "from": "patients",
                "localField": "patient_id",
                "foreignField": "_id",
                "as": "patient"
            }
        },
        {"$unwind": "$patient"},
        {
            "$lookup": {
                "from": "doctors",
                "localField": "doctor_id",
                "foreignField": "_id",
                "as": "doctor"
            }
        },
        {"$unwind": {"path": "$doctor", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 1,
                "appointment_uuid": 1,
                "patient_id": 1,
                "patient": {"name": "$patient.full_name", "phone": "$patient.phone_number"},
                "doctor": {"name": "$doctor.full_name", "specialty": "$doctor.specialty"},
                "doctor_id": 1,
                "appointment_datetime": 1,
                "status": 1,
                "appointment_type": 1,
                "created_at": 1
            }
        },
        {"$sort": {"appointment_datetime": 1}}
    ]
    
    if match_stage:
        pipeline.insert(0, {"$match": match_stage})

    appointments = await db.appointments.aggregate(pipeline).to_list(length=100)
    for apt in appointments:
        apt["_id"] = str(apt["_id"])
        if "appointment_datetime" in apt and hasattr(apt["appointment_datetime"], 'isoformat'):
            apt["appointment_datetime"] = apt["appointment_datetime"].isoformat()
        if "created_at" in apt and hasattr(apt["created_at"], 'isoformat'):
            apt["created_at"] = apt["created_at"].isoformat()
    return appointments

@router.get("/available-slots")
async def fetch_available_slots(
    doctor_id: str,
    target_date: str = Query(..., description="YYYY-MM-DD"),
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """Fetch available slots for a specific doctor on a date."""
    db = get_db()
    try:
        dt_date = date.fromisoformat(target_date)
        slots = await get_available_slots(db, doctor_id, dt_date)
        return {"doctor_id": doctor_id, "date": target_date, "slots": [s.isoformat() for s in slots]}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        logger.error(f"Error fetching slots: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("")
async def create_appointment(appointment: dict, current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """
    Create a new appointment with scheduling validation.
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    # Permission check
    user_role_enum = UserRole(user_role)
    check_resource_access(user_role_enum, ResourceType.APPOINTMENT, ActionType.CREATE, current_user)
    
    # Validate doctor assignment
    if user_role == "doctor":
        appointment["doctor_id"] = current_user["_id"]
    elif user_role == "staff":
        assigned_doctor_id = current_user.get("assigned_doctor_id")
        if not assigned_doctor_id:
            raise HTTPException(status_code=403, detail="Staff not assigned to any doctor")
        appointment["doctor_id"] = ObjectId(assigned_doctor_id)
    else: # admin
        if "doctor_id" not in appointment:
            raise HTTPException(status_code=400, detail="Doctor ID is required")
        appointment["doctor_id"] = ObjectId(appointment["doctor_id"])
    
    appointment["patient_id"] = ObjectId(appointment["patient_id"])
    
    # Parse and validate datetime
    try:
        apt_datetime = datetime.fromisoformat(appointment["appointment_datetime"].replace('Z', ''))
        appointment["appointment_datetime"] = apt_datetime
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid appointment datetime format")

    # SCHEDULING VALIDATION
    is_available = await is_slot_available(db, str(appointment["doctor_id"]), apt_datetime)
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The selected slot is not available for this doctor."
        )

    appointment["created_at"] = datetime.utcnow()
    appointment["status"] = appointment.get("status", "booked")
    
    result = await db.appointments.insert_one(appointment)

    # Send WhatsApp notification
    await notification_service.notify_appointment_created(
        db,
        patient_id=str(appointment["patient_id"]),
        doctor_id=str(appointment["doctor_id"]),
        appointment_datetime=appointment["appointment_datetime"],
        appointment_type=appointment.get("appointment_type", "consultation")
    )

    return {"message": "Appointment created", "id": str(result.inserted_id)}

@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str, current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """Get a specific appointment with full data joins."""
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user_role == "doctor" and str(appointment.get("doctor_id")) != str(current_user.get("_id")):
        raise HTTPException(status_code=403, detail="Cannot access other doctors' appointments")
    elif user_role == "staff" and str(appointment.get("doctor_id")) != str(current_user.get("assigned_doctor_id")):
        raise HTTPException(status_code=403, detail="Cannot access appointments for other doctors")
    
    # Fetch related data
    patient = await db.patients.find_one({"_id": appointment["patient_id"]})
    doctor = await db.doctors.find_one({"_id": appointment["doctor_id"]})
    
    appointment["_id"] = str(appointment["_id"])
    appointment["patient_id"] = str(appointment["patient_id"])
    appointment["doctor_id"] = str(appointment["doctor_id"])
    appointment["patient"] = {"name": patient["full_name"], "phone": patient["phone_number"]} if patient else None
    appointment["doctor"] = {"name": doctor["full_name"], "specialty": doctor["specialty"]} if doctor else None
    
    if "appointment_datetime" in appointment and hasattr(appointment["appointment_datetime"], 'isoformat'):
        appointment["appointment_datetime"] = appointment["appointment_datetime"].isoformat()
    
    return appointment

@router.patch("/{appointment_id}")
async def update_appointment(appointment_id: str, update_data: dict, current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """Update an appointment with scheduling validation."""
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    # Permission check
    user_role_enum = UserRole(user_role)
    check_resource_access(user_role_enum, ResourceType.APPOINTMENT, ActionType.UPDATE, current_user)
    
    # Fetch existing appointment
    appointment = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user_role == "doctor" and str(appointment.get("doctor_id")) != str(current_user.get("_id")):
        raise HTTPException(status_code=403, detail="Doctors can only update their own appointments")
    elif user_role == "staff" and str(appointment.get("doctor_id")) != str(current_user.get("assigned_doctor_id")):
        raise HTTPException(status_code=403, detail="Staff can only update assigned doctor's appointments")
    
    if "appointment_datetime" in update_data:
        new_datetime = datetime.fromisoformat(update_data["appointment_datetime"].replace('Z', ''))
        update_data["appointment_datetime"] = new_datetime
        
        # SCHEDULING VALIDATION
        is_available = await is_slot_available(db, str(appointment["doctor_id"]), new_datetime)
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The new selected slot is not available."
            )
    
    if "patient_id" in update_data:
        update_data["patient_id"] = ObjectId(update_data["patient_id"])
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.appointments.find_one_and_update(
        {"_id": ObjectId(appointment_id)},
        {"$set": update_data},
        return_document=True
    )

    # Send WhatsApp notification
    await notification_service.notify_appointment_updated(
        db,
        patient_id=str(result["patient_id"]),
        doctor_id=str(result["doctor_id"]),
        new_appointment_datetime=result["appointment_datetime"],
        old_appointment_datetime=appointment["appointment_datetime"]
    )

    return {"message": "Appointment updated"}

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: str, current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """Delete an appointment and notify the patient."""
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    # Permission check
    user_role_enum = UserRole(user_role)
    check_resource_access(user_role_enum, ResourceType.APPOINTMENT, ActionType.DELETE, current_user)
    
    # Fetch appointment details
    apt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    if not apt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Check access
    if user_role == "doctor" and str(apt.get("doctor_id")) != str(current_user.get("_id")):
        raise HTTPException(status_code=403, detail="Doctors can only delete their own appointments")
    elif user_role == "staff" and str(apt.get("doctor_id")) != str(current_user.get("assigned_doctor_id")):
        raise HTTPException(status_code=403, detail="Staff can only delete assigned doctor's appointments")
        
    result = await db.appointments.delete_one({"_id": ObjectId(appointment_id)})

    # Send WhatsApp notification
    await notification_service.notify_appointment_cancelled(
        db,
        patient_id=str(apt["patient_id"]),
        doctor_id=str(apt["doctor_id"]),
        cancelled_datetime=apt["appointment_datetime"],
        cancellation_reason="Cancelled by clinic"
    )

    return {"message": "Appointment deleted"}
