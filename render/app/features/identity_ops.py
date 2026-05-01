import json
import uuid
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_phi_db, get_profile_db
from app.logger import logger
from app.core.role_enforcer import RoleEnforcer

async def identify_user(phone_digits: str, normalized_phone: str):
    """
    REVISED: Recognize ONLY Admin/Doctor/Staff.
    Patients are NOT system users and will be REJECTED.
    """
    phi_db = get_phi_db()
    profile_db = get_profile_db()
    
    user_role = None  # Will remain None if user is not authorized
    user_data = None
    
    # Priority Match: Last 10 digits, then 8 digits fallback
    phone_suffix_10 = phone_digits[-10:]
    phone_suffix_8 = phone_digits[-8:]
    
    logger.info(f"[IDENTITY] Checking authorization for suffix: {phone_suffix_8}")

    pattern = {"$regex": phone_suffix_8}
    
    # 1. Check ADMIN (phone numbers in staff table with role=ADMIN)
    admin = await profile_db.staff_users.find_one({
        "phone": pattern,
        "role": {"$in": ["ADMIN", "admin"]}
    })
    if admin:
        user_role = "ADMIN"
        user_data = admin
        logger.info(f"[IDENTITY] ✅ AUTHORIZED: ADMIN {admin['full_name']}")
        return user_role, user_data
    
    # 2. Check STAFF (receptionist, clinic staff)
    staff = await profile_db.staff_users.find_one({
        "phone": pattern,
        "role": {"$in": ["STAFF", "RECEPTIONIST", "staff", "receptionist"]}
    })
    if staff:
        user_role = "STAFF"
        user_data = staff
        logger.info(f"[IDENTITY] ✅ AUTHORIZED: STAFF {staff['full_name']}")
        
        # Get assigned doctor's name for context
        if "assigned_doctor_id" in staff:
            d_id = staff["assigned_doctor_id"]
            if isinstance(d_id, str) and ObjectId.is_valid(d_id):
                d_id = ObjectId(d_id)
            doc = await profile_db.doctors.find_one({"_id": d_id})
            if doc:
                user_data["doctor_name"] = doc["full_name"]
        
        return user_role, user_data
    
    # 3. Check DOCTOR (physicians)
    doctor = await profile_db.doctors.find_one({"whatsapp_number": pattern})
    if doctor:
        user_role = "DOCTOR"
        user_data = doctor
        logger.info(f"[IDENTITY] ✅ AUTHORIZED: DOCTOR {doctor['full_name']}")
        return user_role, user_data
    
    # PATIENTS ARE NOT AUTHORIZED USERS
    # Do not check patient database
    logger.warning(f"[IDENTITY] ❌ REJECTED: No admin/doctor/staff found for {phone_suffix_8}")
    logger.warning(f"[IDENTITY] Patients are NOT system users and cannot access the system.")
    
    return None, None  # No valid user found


async def execute_identity_op(op_type, params, user_data, sender_phone):
    """
    REVISED: Identity operations for ADMIN/DOCTOR/STAFF only.
    Patient self-registration is NOT supported - admins create patient records only.
    """
    if not user_data:
        logger.error("[IDENTITY_OP] Unauthorized: No valid user data")
        return {"error": "Authentication required. Only admin/doctor/staff have access."}
    
    try:
        # Patient registration removed - doctors/staff create records via admin interface
        
        if op_type == "UPDATE_PROFILE":
            # Allow doctor/staff to update own profile
            params["_id"] = user_data["_id"]
            params["updated_at"] = datetime.utcnow()
            
            profile_db = get_profile_db()
            await profile_db.staff_users.update_one(
                {"_id": user_data["_id"]},
                {"$set": params}
            )
            
            logger.info(f"[IDENTITY_OP] Updated profile for {user_data.get('full_name')}")
            return {"status": "success", "message": "Profile updated."}
        
        return {"status": "error", "message": f"Identity operation {op_type} not supported."}
    
    except Exception as e:
        logger.error(f"[IDENTITY_OP_ERROR]: {e}")
        return {"error": str(e)}

