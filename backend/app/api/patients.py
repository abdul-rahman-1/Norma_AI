from fastapi import APIRouter, Depends, HTTPException, Body
from app.db.mongodb import get_db
from app.schemas.models import Patient, PatientBase
from app.core.security import require_role
from app.core.permissions import (
    check_resource_access,
    ResourceType,
    ActionType,
    UserRole
)
from app.services.whatsapp_service import whatsapp_service
from typing import List
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("")
async def get_patients(current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """
    Get list of patients.
    
    Access Control:
    - ADMIN: sees all patients
    - DOCTOR: sees only patients assigned to them
    - STAFF: sees only patients of their assigned doctor
    
    Returns: List of patient objects with medical history
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    try:
        # Convert to UserRole enum for permission checks
        user_role_enum = UserRole(user_role)
        
        # Check resource access permission
        check_resource_access(user_role_enum, ResourceType.PATIENT, ActionType.LIST, current_user)
        
        query = {}
        
        # Apply role-based filtering
        if user_role == "admin":
            # Admin sees all patients
            pass
        elif user_role == "doctor":
            # Doctor sees only patients associated with their appointments or explicitly assigned
            # For now, filter by doctor_id if present in patient record
            query["doctor_id"] = ObjectId(current_user.get("_id"))
        elif user_role == "staff":
            # Staff sees only patients of their assigned doctor
            assigned_doctor_id = current_user.get("assigned_doctor_id")
            if not assigned_doctor_id:
                logger.warning(f"Staff {current_user.get('_id')} has no assigned doctor")
                return []
            query["doctor_id"] = ObjectId(assigned_doctor_id)
        
        # Fetch patients with filters applied
        patients_raw = await db.patients.find(query).to_list(length=200)
        patients = []
        
        for p in patients_raw:
            try:
                # Add doctor information if available
                if p.get("doctor_id"):
                    doctor = await db.doctors.find_one({"_id": ObjectId(p["doctor_id"])})
                    if doctor:
                        p["doctor"] = {
                            "id": str(doctor["_id"]),
                            "name": doctor.get("full_name", "N/A"),
                            "specialty": doctor.get("specialty", "N/A")
                        }
                
                patients.append(Patient(**p))
            except Exception as e:
                logger.warning(f"Skipping invalid patient: {p.get('_id')}. Error: {e}")
                continue
        
        logger.info(f"{user_role} {current_user.get('username')} listed {len(patients)} patients")
        return patients
    
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching patients")


@router.post("")
async def create_patient(
    patient: PatientBase,
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Create a new patient record.
    
    Access Control:
    - ADMIN: can create patients for any doctor
    - DOCTOR: can create patients for themselves
    - STAFF: can create patients for their assigned doctor
    
    Returns: Created patient object
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    try:
        # Check resource access permission
        user_role_enum = UserRole(user_role)
        check_resource_access(user_role_enum, ResourceType.PATIENT, ActionType.CREATE, current_user)
        
        patient_dict = patient.dict()
        patient_dict["created_by"] = ObjectId(current_user["_id"])
        patient_dict["created_at"] = patient_dict["updated_at"] = datetime.utcnow()
        
        # Assign to appropriate doctor based on role
        if user_role == "admin":
            # Admin specifies doctor_id or uses provided value
            if not patient_dict.get("doctor_id"):
                raise HTTPException(status_code=400, detail="Admin must specify doctor_id")
            patient_dict["doctor_id"] = ObjectId(patient_dict["doctor_id"])
        
        elif user_role == "doctor":
            # Doctor creates patient for themselves
            patient_dict["doctor_id"] = ObjectId(current_user["_id"])
        
        elif user_role == "staff":
            # Staff creates patient for their assigned doctor
            assigned_doctor_id = current_user.get("assigned_doctor_id")
            if not assigned_doctor_id:
                raise HTTPException(status_code=403, detail="Staff must be assigned to a doctor")
            patient_dict["doctor_id"] = ObjectId(assigned_doctor_id)
        
        result = await db.patients.insert_one(patient_dict)
        patient_dict["_id"] = result.inserted_id
        
        # Send WhatsApp registration confirmation
        try:
            await whatsapp_service.send_registration_confirmation(
                to_phone=patient.phone_number,
                patient_name=patient.full_name,
                patient_uuid=patient_dict.get("patient_uuid")
            )
        except Exception as e:
            logger.warning(f"Failed to send registration WhatsApp: {e}")
        
        logger.info(f"{user_role} {current_user.get('username')} created patient {patient_dict['_id']}")
        return patient_dict
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating patient")


@router.get("/{patient_id}")
async def get_patient(
    patient_id: str,
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Get specific patient details.
    
    Access Control:
    - ADMIN: can view any patient
    - DOCTOR: can view only their own patients
    - STAFF: can view only patients of their assigned doctor
    
    Returns: Patient object with full medical history
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    try:
        # Check resource access permission
        user_role_enum = UserRole(user_role)
        check_resource_access(user_role_enum, ResourceType.PATIENT, ActionType.READ, current_user)
        
        patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Verify access based on role
        if user_role == "doctor":
            if str(patient.get("doctor_id")) != str(current_user.get("_id")):
                raise HTTPException(status_code=403, detail="Cannot access other doctors' patients")
        
        elif user_role == "staff":
            assigned_doctor_id = current_user.get("assigned_doctor_id")
            if not assigned_doctor_id or str(patient.get("doctor_id")) != str(assigned_doctor_id):
                raise HTTPException(status_code=403, detail="Cannot access patients outside assigned doctor")
        
        # Add doctor information
        if patient.get("doctor_id"):
            doctor = await db.doctors.find_one({"_id": ObjectId(patient["doctor_id"])})
            if doctor:
                patient["doctor"] = {
                    "id": str(doctor["_id"]),
                    "name": doctor.get("full_name", "N/A"),
                    "specialty": doctor.get("specialty", "N/A")
                }
        
        logger.info(f"{user_role} {current_user.get('username')} viewed patient {patient_id}")
        return patient
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{patient_id}")
async def update_patient(
    patient_id: str,
    patient_update: dict,
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Update patient information.
    
    Access Control:
    - ADMIN: can update any patient
    - DOCTOR: can update only their own patients
    - STAFF: can update only patients of their assigned doctor
    
    Returns: Updated patient object
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    try:
        # Check resource access permission
        user_role_enum = UserRole(user_role)
        check_resource_access(user_role_enum, ResourceType.PATIENT, ActionType.UPDATE, current_user)
        
        # Get patient to verify access
        patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Verify access based on role
        if user_role == "doctor":
            if str(patient.get("doctor_id")) != str(current_user.get("_id")):
                raise HTTPException(status_code=403, detail="Cannot update other doctors' patients")
        
        elif user_role == "staff":
            assigned_doctor_id = current_user.get("assigned_doctor_id")
            if not assigned_doctor_id or str(patient.get("doctor_id")) != str(assigned_doctor_id):
                raise HTTPException(status_code=403, detail="Cannot update patients outside assigned doctor")
        
        # Prevent certain fields from being updated
        patient_update.pop("_id", None)
        patient_update.pop("created_by", None)
        patient_update.pop("created_at", None)
        patient_update["updated_at"] = datetime.utcnow()
        
        result = await db.patients.find_one_and_update(
            {"_id": ObjectId(patient_id)},
            {"$set": patient_update},
            return_document=True
        )
        
        logger.info(f"{user_role} {current_user.get('username')} updated patient {patient_id}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Delete a patient record.
    
    CAUTION: This is a soft or hard delete depending on business logic.
    
    Access Control:
    - ADMIN: can delete any patient
    - DOCTOR: can delete only their own patients
    - STAFF: cannot delete patients (ADMIN only)
    
    Returns: Confirmation message
    """
    db = get_db()
    user_role = current_user.get("role", "").lower()
    
    try:
        # Only admin and doctors can delete
        if user_role == "staff":
            raise HTTPException(status_code=403, detail="Staff cannot delete patient records")
        
        # Check resource access permission
        user_role_enum = UserRole(user_role)
        check_resource_access(user_role_enum, ResourceType.PATIENT, ActionType.DELETE, current_user)
        
        # Get patient to verify access
        patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Verify access
        if user_role == "doctor":
            if str(patient.get("doctor_id")) != str(current_user.get("_id")):
                raise HTTPException(status_code=403, detail="Cannot delete other doctors' patients")
        
        # Perform soft delete (mark as inactive)
        result = await db.patients.find_one_and_update(
            {"_id": ObjectId(patient_id)},
            {
                "$set": {
                    "is_active": False,
                    "deleted_at": datetime.utcnow(),
                    "deleted_by": ObjectId(current_user["_id"])
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        logger.info(f"{user_role} {current_user.get('username')} deleted patient {patient_id}")
        return {"message": "Patient record deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


