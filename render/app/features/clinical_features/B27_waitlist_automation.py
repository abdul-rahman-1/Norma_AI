from datetime import datetime
from app.db.mongodb import get_phi_db
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B27: Waitlist Automation
    Queue management for patients wanting earlier slots.
    """
    allowed = ["PATIENT", "STAFF", "ADMIN", "DOCTOR"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B27_WAITLIST_AUTOMATION")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    phi_db = get_phi_db()
    try:
        patient_id = params.get("patient_id") or (user_data["_id"] if user_data and user_role == "PATIENT" else None)
        doctor_id = params.get("doctor_id")
        action = params.get("action", "JOIN") # JOIN, LEAVE, LIST

        if not patient_id or not doctor_id:
            return {"status": "error", "message": "Patient ID and Doctor ID are required."}

        if action == "JOIN":
            waitlist_entry = {
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "preferred_days": params.get("preferred_days", []),
                "joined_at": datetime.utcnow(),
                "status": "waiting"
            }
            # Save to waitlist collection
            await phi_db.waitlist.update_one(
                {"patient_id": patient_id, "doctor_id": doctor_id},
                {"$set": waitlist_entry},
                upsert=True
            )
            return {"status": "success", "message": "You have been added to the waitlist."}

        elif action == "LIST":
            # For staff/doctors to see the queue
            queue = await phi_db.waitlist.find({"doctor_id": doctor_id, "status": "waiting"}).sort("joined_at", 1).to_list(length=50)
            return {"status": "success", "queue_length": len(queue), "queue": queue}

        return {"status": "error", "message": f"Action {action} not supported."}

    except Exception as e:
        logger.error(f"B27_WAITLIST_ERROR: {str(e)}")
        return {"status": "error", "message": f"Waitlist operation failed: {str(e)}"}
