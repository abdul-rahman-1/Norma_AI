from datetime import datetime, timedelta
from app.db.mongodb import get_phi_db, get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B22: Next Patient Prep
    1h context alerts for doctors and reminders for patients.
    """
    # This is typically an automated background task, but can be triggered manually by staff/admins
    allowed = ["DOCTOR", "ADMIN", "STAFF", "SYSTEM"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B22_NEXT_PATIENT_PREP")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    phi_db = get_phi_db()
    profile_db = get_profile_db()
    try:
        # Check for appointments happening in exactly 1 hour or as specified in params
        hours_ahead = params.get("hours_ahead", 1)
        target_time = (datetime.utcnow() + timedelta(hours=hours_ahead)).strftime("%Y-%m-%d %H:%M")
        
        apts = await phi_db.appointments.find({
            "appointment_datetime": {"$regex": f"^{target_time}"}, 
            "status": "scheduled", 
            "prep_reminder_sent": {"$ne": True}
        }).to_list(length=20)
        
        results = []
        for a in apts:
            patient = await phi_db.patients.find_one({"_id": a["patient_id"]})
            doctor = await profile_db.doctors.find_one({"_id": a["doctor_id"]})
            
            if patient and doctor:
                # 1. Alert Patient (A4 reminder logic)
                patient_msg = f"🔔 *Appointment Reminder*\nHi {patient['full_name']}, your visit with {doctor['full_name']} is in {hours_ahead} hour(s) ({a['appointment_datetime']}). See you soon!"
                await whatsapp_service.send_custom_message(patient["phone_number"], patient_msg)
                
                # 2. Alert Doctor with Prep Context (B22)
                if doctor.get("whatsapp_number"):
                    doc_msg = (
                        f"👨‍⚕️ *Next Patient Context*\n"
                        f"Patient: {patient['full_name']}\n"
                        f"Time: {a['appointment_datetime']}\n"
                        f"Reason: {a.get('chief_complaint', 'General Follow-up')}\n"
                        f"Alerts: {patient.get('medical_alerts', 'None')}"
                    )
                    await whatsapp_service.send_custom_message(doctor["whatsapp_number"], doc_msg)
                
                # Mark as sent
                await phi_db.appointments.update_one({"_id": a["_id"]}, {"$set": {"prep_reminder_sent": True}})
                logger.info(f"B22: Sent prep alerts for {patient['full_name']} / {doctor['full_name']}")
                results.append({"appointment_id": str(a["_id"]), "status": "sent"})

        return {"status": "success", "processed_count": len(results), "results": results}

    except Exception as e:
        logger.error(f"B22_NEXT_PATIENT_PREP_ERROR: {str(e)}")
        return {"status": "error", "message": f"Prep alert failed: {str(e)}"}
