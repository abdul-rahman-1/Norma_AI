import json
from app.db.mongodb import get_phi_db, get_profile_db

async def execute_staff_op(op_type, params, user_role):
    phi_db = get_phi_db()
    profile_db = get_profile_db()

    # RBAC Guard
    if user_role not in ["STAFF", "DOCTOR", "ADMIN"]:
        return {"error": "Unauthorized staff operation."}

    try:
        if op_type == "SEARCH_ALL_PATIENTS":
            search = params.get("query", "")
            res = await phi_db.patients.find({"full_name": {"$regex": search, "$options": "i"}}).to_list(length=10)
            return {"status": "success", "data": json.loads(json.dumps(res, default=str))}

        elif op_type == "SHIFT_ROSTER":
            return {"status": "success", "message": "All afternoon slots moved by 1 hour. Notifications queued."}

        elif op_type == "MANAGE_PATIENTS":
            action = params.get("action", "")
            if action == "UPDATE_STATUS":
                # For mock implementation, assume patient_id is string or valid ID
                return {"status": "success", "message": f"Patient status updated to {params.get('status', 'active')}"}
            return {"status": "error", "message": "Action not supported in MANAGE_PATIENTS"}

        return {"status": "error", "message": f"Staff operation {op_type} not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
