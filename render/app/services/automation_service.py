import asyncio
from datetime import datetime, timedelta
from app.db.mongodb import get_phi_db, get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.logger import logger
import json

class AutomationService:
    async def send_doctor_daily_briefing(self):
        """Action B21: Sends a detailed clinical summary of the day to all active doctors."""
        profile_db = get_profile_db()
        phi_db = get_phi_db()
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            doctors = await profile_db.doctors.find({"is_active": True}).to_list(length=50)
            
            for doc in doctors:
                if not doc.get("whatsapp_number"): continue
                
                # Fetch all scheduled appointments for today
                apts = await phi_db.appointments.find({
                    "doctor_id": doc["_id"], 
                    "appointment_datetime": {"$regex": f"^{today}"},
                    "status": "scheduled"
                }).sort("appointment_datetime", 1).to_list(length=50)
                
                if not apts:
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
                logger.info(f"[AUTO] Sent daily briefing to {doc['full_name']}")
                
        except Exception as e:
            logger.error(f"BRIEFING_ERROR: {e}")

    async def run_proactive_alerts(self):
        """Action B22: Medical record prep for doctors 1 hour before appointment."""
        phi_db = get_phi_db()
        profile_db = get_profile_db()
        try:
            # Check for appointments happening in exactly 1 hour
            target_time = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            apts = await phi_db.appointments.find({
                "appointment_datetime": {"$regex": f"^{target_time}"}, 
                "status": "scheduled", 
                "doctor_prep_sent": {"$ne": True}
            }).to_list(length=20)
            
            for a in apts:
                patient = await phi_db.patients.find_one({"_id": a["patient_id"]})
                doctor = await profile_db.doctors.find_one({"_id": a["doctor_id"]})
                
                if patient and doctor:
                    # Alert Doctor with Prep Context (B22)
                    doc_msg = (
                        f"👨‍⚕️ *Next Patient Context*\n"
                        f"Patient: {patient['full_name']}\n"
                        f"Time: {a['appointment_datetime']}\n"
                        f"Reason: {a.get('chief_complaint', 'General Follow-up')}\n"
                        f"Alerts: {patient.get('medical_alerts', 'None')}"
                    )
                    await whatsapp_service.send_custom_message(doctor["whatsapp_number"], doc_msg)
                    
                    # Mark as sent
                    await phi_db.appointments.update_one({"_id": a["_id"]}, {"$set": {"doctor_prep_sent": True}})
                    logger.info(f"[AUTO] Sent doctor prep for {patient['full_name']} / {doctor['full_name']}")

        except Exception as e:
            logger.error(f"ALERT_ERROR: {e}")

    # async def send_24h_reminders(self):
    #     """Action A4: Removed (Patient-facing)"""
    #     pass

automation_service = AutomationService()
