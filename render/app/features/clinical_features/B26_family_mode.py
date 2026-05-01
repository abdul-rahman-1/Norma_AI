from datetime import datetime
import uuid
from app.db.mongodb import get_phi_db
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B26: Family Mode
    Multiple patients per phone number.
    """
    allowed = ["PATIENT", "DOCTOR", "STAFF", "ADMIN"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B26_FAMILY_MODE")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    phi_db = get_phi_db()
    try:
        phone = params.get("phone_number") or sender_phone
        action = params.get("action", "LIST") # LIST, ADD, SWITCH

        if not phone:
            return {"status": "error", "message": "Phone number is required."}

        if action == "LIST":
            # Find all patients with this phone number
            family_members = await phi_db.patients.find({"phone_number": phone}).to_list(length=10)
            return {
                "status": "success",
                "count": len(family_members),
                "members": [
                    {"patient_uuid": m.get("patient_uuid"), "full_name": m.get("full_name")} 
                    for m in family_members
                ]
            }

        elif action == "ADD":
            # Add a new family member to this phone number
            full_name = params.get("full_name")
            if not full_name:
                return {"status": "error", "message": "Full name is required to add a family member."}

            new_member = {
                "patient_uuid": str(uuid.uuid4()),
                "full_name": full_name,
                "phone_number": phone,
                "relationship": params.get("relationship", "Dependent"),
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            await phi_db.patients.insert_one(new_member)
            return {
                "status": "success",
                "message": f"Added {full_name} as a family member.",
                "patient_uuid": new_member["patient_uuid"]
            }

        return {"status": "error", "message": f"Action {action} not supported in Family Mode."}

    except Exception as e:
        logger.error(f"B26_FAMILY_MODE_ERROR: {str(e)}")
        return {"status": "error", "message": f"Family Mode operation failed: {str(e)}"}
