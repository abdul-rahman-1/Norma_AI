from datetime import datetime
from app.db.mongodb import get_phi_db, get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B21: Daily Briefing
    Sends a detailed clinical summary of the day to all active doctors.
    """
    allowed = ["DOCTOR", "ADMIN", "STAFF"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B21_DAILY_BRIEFING")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    profile_db = get_profile_db()
    phi_db = get_phi_db()
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # If doctor_id is provided in params, only send to that doctor. Otherwise send to all.
        target_doctor_id = params.get("doctor_id")
        query = {"is_active": True}
        if target_doctor_id:
            query["_id"] = target_doctor_id

        doctors = await profile_db.doctors.find(query).to_list(length=50)
        
        results = []
        for doc in doctors:
            if not doc.get("whatsapp_number"): continue
            
            # Fetch all scheduled appointments for today
            apts = await phi_db.appointments.find({
                "doctor_id": doc["_id"], 
                "appointment_datetime": {"$regex": f"^{today}"},
                "status": "scheduled"
            }).sort("appointment_datetime", 1).to_list(length=50)
            
            if not apts:
                results.append({"doctor": doc["full_name"], "status": "skipped", "reason": "No appointments"})
                continue

            msg = f"🏥 *Morning Briefing: {doc['full_name']}*\n"
            msg += f"📅 Today, {today}, you have {len(apts)} patients scheduled.\n\n"
            
            for a in apts:
                patient = await phi_db.patients.find_one({"_id": a["patient_id"]})
                time = a["appointment_datetime"].split(" ")[1]
                p_name = patient["full_name"] if patient else "Unknown"
                msg += f"• {time}: {p_name} ({a.get('appointment_type', 'Consultation')})\n"
            
            msg += "\nGood luck with your rounds today!"
            await whatsapp_service.send_custom_message(doc["whatsapp_number"], msg)
            logger.info(f"B21: Sent daily briefing to {doc['full_name']}")
            results.append({"doctor": doc["full_name"], "status": "sent", "count": len(apts)})
            
        return {"status": "success", "results": results}
    except Exception as e:
        logger.error(f"B21_DAILY_BRIEFING_ERROR: {str(e)}")
        return {"status": "error", "message": f"Briefing failed: {str(e)}"}
