from datetime import datetime, timedelta
from app.db.mongodb import get_phi_db
from app.services.whatsapp_service import whatsapp_service
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B29: Post-Op Followup
    Automated follow-up pings for patients after procedures.
    """
    allowed = ["DOCTOR", "STAFF", "ADMIN", "SYSTEM"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B29_POST_OP_FOLLOWUP")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    phi_db = get_phi_db()
    try:
        # This can be triggered for a specific patient or as a batch for recent surgeries
        patient_id = params.get("patient_id")
        procedure_name = params.get("procedure_name", "your recent procedure")
        
        if patient_id:
            patient = await phi_db.patients.find_one({"_id": patient_id})
            if not patient or not patient.get("phone_number"):
                return {"status": "error", "message": "Patient not found or has no phone number."}

            msg = (
                f"👋 *How are you feeling?*\n"
                f"Hi {patient['full_name']}, this is a follow-up check-in from the clinic regarding your {procedure_name}.\n\n"
                f"How is your recovery going? Please reply with a number:\n"
                f"1. Feeling Great\n"
                f"2. Some Discomfort\n"
                f"3. Need to speak with a nurse"
            )
            await whatsapp_service.send_custom_message(patient["phone_number"], msg)
            
            # Log the follow-up
            await phi_db.communications.insert_one({
                "patient_id": patient_id,
                "type": "post_op_followup",
                "procedure": procedure_name,
                "sent_at": datetime.utcnow()
            })
            
            return {"status": "success", "message": f"Follow-up sent to {patient['full_name']}."}

        return {"status": "error", "message": "Patient ID is required for post-op follow-up."}

    except Exception as e:
        logger.error(f"B29_POST_OP_FOLLOWUP_ERROR: {str(e)}")
        return {"status": "error", "message": f"Follow-up failed: {str(e)}"}
