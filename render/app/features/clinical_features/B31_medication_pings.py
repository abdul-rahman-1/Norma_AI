from datetime import datetime
from app.db.mongodb import get_phi_db
from app.services.whatsapp_service import whatsapp_service
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B31: Medication Pings
    Automated prescription reminders for patients.
    """
    allowed = ["PATIENT", "DOCTOR", "STAFF", "ADMIN", "SYSTEM"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B31_MEDICATION_PINGS")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    phi_db = get_phi_db()
    try:
        patient_id = params.get("patient_id") or (user_data["_id"] if user_data and user_role == "PATIENT" else None)
        
        if not patient_id:
            return {"status": "error", "message": "Patient ID is required."}

        patient = await phi_db.patients.find_one({"_id": patient_id})
        if not patient or not patient.get("phone_number"):
            return {"status": "error", "message": "Patient not found or has no phone number."}

        # Fetch active prescriptions
        prescriptions = await phi_db.prescriptions.find({
            "patient_id": patient_id,
            "status": "active"
        }).to_list(length=20)

        if not prescriptions:
            return {"status": "success", "message": "No active prescriptions found for this patient."}

        results = []
        for p in prescriptions:
            med_name = p.get("medication_name")
            dosage = p.get("dosage")
            schedule = p.get("schedule", "as directed")
            
            msg = (
                f"💊 *Medication Reminder*\n"
                f"Hi {patient['full_name']}, it's time for your medication:\n"
                f"*Medication:* {med_name}\n"
                f"*Dosage:* {dosage}\n"
                f"*Schedule:* {schedule}\n\n"
                f"Please reply 'Taken' once you have taken it."
            )
            await whatsapp_service.send_custom_message(patient["phone_number"], msg)
            
            # Log the reminder
            await phi_db.communications.insert_one({
                "patient_id": patient_id,
                "prescription_id": p["_id"],
                "type": "medication_reminder",
                "sent_at": datetime.utcnow()
            })
            results.append({"medication": med_name, "status": "sent"})

        return {"status": "success", "reminders_sent": len(results), "results": results}

    except Exception as e:
        logger.error(f"B31_MEDICATION_PINGS_ERROR: {str(e)}")
        return {"status": "error", "message": f"Medication pings failed: {str(e)}"}
