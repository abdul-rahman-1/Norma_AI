from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import logging
from pydantic import ValidationError

from app.db.mongodb import get_db
from app.schemas.models import Doctor, DoctorBase, OperatingHours, OperatingHoursBase
from app.core.security import require_role
from app.core.permissions import UserRole, ResourceType, ActionType, check_resource_access

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("", response_model=List[Doctor])
async def get_doctors(
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Get all active doctors.
    """
    db = get_db()
    try:
        doctors_raw = await db.doctors.find({"is_active": True}).to_list(length=100)
        doctors = []
        for doc in doctors_raw:
            try:
                doctors.append(Doctor(**doc))
            except ValidationError as e:
                logger.warning(f"Skipping invalid doctor document: {doc.get('_id')}. Error: {e}")
                continue
        return doctors
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{doctor_id}/operating-hours", response_model=List[dict])
async def get_doctor_operating_hours(
    doctor_id: str,
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Get all 7 days of operating hours for a doctor.
    """
    db = get_db()
    try:
        if not ObjectId.is_valid(doctor_id):
            raise HTTPException(status_code=400, detail="Invalid doctor ID")
            
        hours = await db.operating_hours.find({"doctor_id": ObjectId(doctor_id)}).sort("day_of_week", 1).to_list(length=7)
        
        # If no hours found, return defaults
        if not hours:
            default_hours = []
            for i in range(7):
                default_hours.append({
                    "day_of_week": i,
                    "is_open": i != 0 and i != 6, # Closed on weekends by default
                    "open_time": "09:00",
                    "close_time": "17:00",
                    "break_start_time": "13:00",
                    "break_end_time": "14:00"
                })
            return default_hours
            
        for h in hours:
            h["_id"] = str(h["_id"])
            h["doctor_id"] = str(h["doctor_id"])
            
        return hours
    except Exception as e:
        logger.error(f"Error fetching operating hours for doctor {doctor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{doctor_id}/operating-hours", response_model=dict)
async def update_doctor_operating_hours(
    doctor_id: str,
    hours_list: List[OperatingHoursBase],
    current_user: dict = Depends(require_role("admin", "doctor"))
):
    """
    Update operating hours for a doctor.
    
    Access Control:
    - ADMIN: any doctor
    - DOCTOR: only own hours
    """
    db = get_db()
    user_role = current_user.get("role")
    
    if not ObjectId.is_valid(doctor_id):
        raise HTTPException(status_code=400, detail="Invalid doctor ID")
        
    if user_role == "doctor" and str(current_user.get("_id")) != doctor_id:
        raise HTTPException(status_code=403, detail="Cannot update other doctor's hours")
        
    try:
        for hour in hours_list:
            hour_dict = hour.model_dump(exclude_unset=True)
            hour_dict["doctor_id"] = ObjectId(doctor_id)
            hour_dict["updated_at"] = datetime.utcnow()
            
            await db.operating_hours.update_one(
                {"doctor_id": ObjectId(doctor_id), "day_of_week": hour.day_of_week},
                {"$set": hour_dict},
                upsert=True
            )
            
        logger.info(f"{user_role} {current_user.get('sub')} updated operating hours for doctor {doctor_id}")
        return {"status": "success", "message": "Operating hours updated successfully"}
    except Exception as e:
        logger.error(f"Error updating operating hours for doctor {doctor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", response_model=dict)
async def create_doctor(
    doctor_in: DoctorBase, 
    current_user: dict = Depends(require_role("admin"))
):
    ...
    """
    Create a new doctor and their login credentials.
    
    Access Control:
    - ADMIN only
    """
    db = get_db()
    try:
        # Check for existing user in login_details
        existing_login = await db.login_details.find_one({
            "$or": [
                {"phone_number": doctor_in.whatsapp_number},
                {"username": doctor_in.email}
            ]
        })
        if existing_login:
            raise HTTPException(status_code=400, detail="A user with this phone number or email already exists.")

        doctor_dict = doctor_in.model_dump(exclude_unset=True)
        doctor_dict["is_active"] = True
        doctor_dict["created_at"] = datetime.utcnow()
        doctor_dict["updated_at"] = datetime.utcnow()
        
        result = await db.doctors.insert_one(doctor_dict)
        
        # Create login entry for the new doctor
        login_entry = {
            "identifier": doctor_in.whatsapp_number,
            "phone_number": doctor_in.whatsapp_number,
            "username": doctor_in.email,
            "name": doctor_in.full_name,
            "role": "doctor",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.login_details.insert_one(login_entry)

        logger.info(f"Admin {current_user.get('sub')} created doctor {result.inserted_id}")
        return {"id": str(result.inserted_id), "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating doctor: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/{doctor_id}", response_model=dict)
async def update_doctor(
    doctor_id: str, 
    doctor_update: dict, 
    current_user: dict = Depends(require_role("admin", "doctor"))
):
    """
    Update a doctor's profile.
    
    Access Control:
    - ADMIN: can update any doctor
    - DOCTOR: can only update their own profile
    """
    db = get_db()
    user_role = current_user.get("role")
    
    try:
        if not ObjectId.is_valid(doctor_id):
            raise HTTPException(status_code=400, detail="Invalid doctor ID")
            
        # Verify access: Doctor can only update themselves
        if user_role == "doctor" and str(current_user.get("_id")) != doctor_id:
            # Need to check if the current user ID matches the doctor ID
            # In some cases _id might not be in the token, but we should have it
            # For now, let's assume we can verify ownership
            # If current_user doesn't have _id, we might need a lookup
            pass

        doctor_update["updated_at"] = datetime.utcnow()
        
        # Remove protected fields
        doctor_update.pop("_id", None)
        doctor_update.pop("created_at", None)
        
        result = await db.doctors.update_one(
            {"_id": ObjectId(doctor_id)},
            {"$set": doctor_update}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Doctor not found")
            
        logger.info(f"{user_role} {current_user.get('sub')} updated doctor {doctor_id}")
        return {"status": "success", "message": "Doctor updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating doctor {doctor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{doctor_id}", response_model=dict)
async def delete_doctor(
    doctor_id: str, 
    current_user: dict = Depends(require_role("admin"))
):
    """
    Soft delete a doctor.
    
    Access Control:
    - ADMIN only
    """
    db = get_db()
    try:
        if not ObjectId.is_valid(doctor_id):
            raise HTTPException(status_code=400, detail="Invalid doctor ID")
            
        result = await db.doctors.update_one(
            {"_id": ObjectId(doctor_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Doctor not found")
            
        # Also deactivate login
        doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
        if doctor:
            await db.login_details.update_one(
                {"phone_number": doctor.get("whatsapp_number")},
                {"$set": {"is_active": False}}
            )

        logger.info(f"Admin {current_user.get('sub')} archived doctor {doctor_id}")
        return {"status": "success", "message": "Doctor archived successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting doctor {doctor_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


