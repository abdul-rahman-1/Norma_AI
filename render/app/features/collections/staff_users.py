import json
from datetime import datetime
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "user_uuid", "full_name", "email", "phone", "whatsapp_number", "password_hash", "role", "permissions", "is_active", "last_login", "created_at", "updated_at" }

from app.core.security import enforce_role, RBAC_PERMISSIONS

async def handle_staff_users(op_type, params, user_role="PATIENT"):
    db = get_profile_db()
    
    # RBAC: Only DOCTOR or ADMIN can manage staff
    allowed = RBAC_PERMISSIONS.get("MANAGE_STAFF", ["DOCTOR"])
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name=op_type)
    if not is_authorized:
        return {"error": err_msg}

    try:
        if op_type == "GET":
            res = await db.staff_users.find_one(params)
            return json.loads(json.dumps(res, default=str))
        
        elif op_type == "CREATE":
            params["created_at"] = datetime.utcnow()
            params["updated_at"] = datetime.utcnow()
            params["is_active"] = True
            await db.staff_users.insert_one(params)
            return {"status": "success", "message": "Staff member authorized."}

        elif op_type == "UPDATE":
            query = {"user_uuid": params.pop("user_uuid")}
            params["updated_at"] = datetime.utcnow()
            await db.staff_users.update_one(query, {"$set": params})
            return {"status": "success", "message": "Staff record updated."}
            
        elif op_type == "LIST":
            res = await db.staff_users.find({}).to_list(length=50)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
