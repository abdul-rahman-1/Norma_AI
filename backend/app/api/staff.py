from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime
import logging

from app.db.mongodb import get_db
from app.core.security import require_role
from app.core.permissions import UserRole, ResourceType, ActionType, check_resource_access
from app.schemas.staff import Staff, StaffCreate, StaffUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/staff", tags=["staff"])

@router.post("", response_model=Staff)
async def create_staff(
    staff_in: StaffCreate,
    current_user: dict = Depends(require_role("admin", "doctor"))
):
    """
    Create a new staff member.
    
    Access Control:
    - ADMIN: can create staff for any doctor
    - DOCTOR: can create staff for themselves
    """
    db = get_db()
    user_role = current_user.get("role")
    
    try:
        # Check for existing user in login_details
        existing_login = await db.login_details.find_one({
            "$or": [
                {"phone_number": staff_in.phone_number},
                {"username": staff_in.email}
            ]
        })
        if existing_login:
            raise HTTPException(status_code=400, detail="A user with this phone number or email already exists.")

        if user_role == "doctor":
            staff_in.doctor_id = str(current_user.get("_id"))
        elif user_role == "admin" and not staff_in.doctor_id:
            raise HTTPException(status_code=400, detail="Admin must provide a doctor_id for the staff.")

        staff_dict = staff_in.model_dump(exclude_unset=True)
        staff_dict["is_active"] = True
        staff_dict["created_at"] = datetime.utcnow()
        staff_dict["updated_at"] = datetime.utcnow()

        result = await db.staff_users.insert_one(staff_dict)
        
        # Create login entry
        login_entry = {
            "identifier": staff_in.phone_number,
            "phone_number": staff_in.phone_number,
            "username": staff_in.email,
            "name": staff_in.full_name,
            "role": "staff",
            "assigned_doctor_id": staff_in.doctor_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.login_details.insert_one(login_entry)

        created_staff = await db.staff_users.find_one({"_id": result.inserted_id})
        logger.info(f"{user_role} {current_user.get('sub')} created staff {result.inserted_id}")
        return Staff(**created_staff, id=result.inserted_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating staff: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("", response_model=List[Staff])
async def get_all_staff(
    current_user: dict = Depends(require_role("admin", "doctor"))
):
    """
    Get all staff members.
    
    Access Control:
    - ADMIN: sees all staff
    - DOCTOR: sees only their own staff
    """
    db = get_db()
    user_role = current_user.get("role")
    query = {"is_active": True}
    
    if user_role == "doctor":
        query["doctor_id"] = str(current_user.get("_id"))
    
    try:
        staff_list_cursor = db.staff_users.find(query)
        staff_list = []
        async for staff_member in staff_list_cursor:
            staff_list.append(Staff(**staff_member, id=staff_member["_id"]))
        return staff_list
    except Exception as e:
        logger.error(f"Error fetching staff list: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/{staff_id}", response_model=Staff)
async def update_staff(
    staff_id: str,
    staff_update: StaffUpdate,
    current_user: dict = Depends(require_role("admin", "doctor"))
):
    """
    Update staff member details.
    
    Access Control:
    - ADMIN: can update any staff
    - DOCTOR: can update only their own staff
    """
    db = get_db()
    if not ObjectId.is_valid(staff_id):
        raise HTTPException(status_code=400, detail="Invalid Staff ID")
    
    oid = ObjectId(staff_id)
    try:
        existing_staff = await db.staff_users.find_one({"_id": oid})
        if not existing_staff:
            raise HTTPException(status_code=404, detail="Staff not found")

        user_role = current_user.get("role")
        if user_role == "doctor" and existing_staff.get("doctor_id") != str(current_user.get("_id")):
            raise HTTPException(status_code=403, detail="Not authorized to update this staff member")

        update_data = staff_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await db.staff_users.update_one({"_id": oid}, {"$set": update_data})
        
        # Also update login_details if phone/name/email changed
        if any(k in update_data for k in ["phone_number", "full_name", "email"]):
            login_update = {}
            if "phone_number" in update_data: login_update["phone_number"] = update_data["phone_number"]
            if "full_name" in update_data: login_update["name"] = update_data["full_name"]
            if "email" in update_data: login_update["username"] = update_data["email"]
            
            await db.login_details.update_one(
                {"phone_number": existing_staff["phone_number"]},
                {"$set": login_update}
            )

        updated_staff = await db.staff_users.find_one({"_id": oid})
        logger.info(f"{user_role} {current_user.get('sub')} updated staff {staff_id}")
        return Staff(**updated_staff, id=oid)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating staff {staff_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{staff_id}", status_code=204)
async def delete_staff(
    staff_id: str,
    current_user: dict = Depends(require_role("admin", "doctor"))
):
    """
    Soft delete a staff member.
    
    Access Control:
    - ADMIN: can delete any staff
    - DOCTOR: can delete only their own staff
    """
    db = get_db()
    if not ObjectId.is_valid(staff_id):
        raise HTTPException(status_code=400, detail="Invalid Staff ID")

    oid = ObjectId(staff_id)
    try:
        existing_staff = await db.staff_users.find_one({"_id": oid})
        if not existing_staff:
            raise HTTPException(status_code=404, detail="Staff not found")

        user_role = current_user.get("role")
        if user_role == "doctor" and existing_staff.get("doctor_id") != str(current_user.get("_id")):
            raise HTTPException(status_code=403, detail="Not authorized to delete this staff member")

        # Soft delete
        await db.staff_users.update_one(
            {"_id": oid}, 
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        # Deactivate login
        await db.login_details.update_one(
            {"phone_number": existing_staff["phone_number"]},
            {"$set": {"is_active": False}}
        )
        
        logger.info(f"{user_role} {current_user.get('sub')} archived staff {staff_id}")
        return {}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting staff {staff_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
