import asyncio
from datetime import datetime, timedelta
from app.db.mongodb import get_phi_db, get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.logger import logger
import json

class AutomationService:
    async def send_doctor_daily_briefing(self):
        """Sends a morning summary to all active doctors about their daily schedule."""
        profile_db = get_profile_db()
        phi_db = get_phi_db()
        
        try:
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            doctors = await profile_db.doctors.find({"is_active": True}).to_list(length=100)
            
            for doc in doctors:
                if not doc.get("whatsapp_number"): continue
                
                # Find all appointments for this doctor today
                apts = await phi_db.appointments.find({
                    "doctor_id": doc["_id"],
                    "appointment_datetime": {"$regex": f"^{today_str}"},
                    "status": "scheduled"
                }).sort("appointment_datetime", 1).to_list(length=50)
                
                if not apts: continue
                
                summary = f"Good morning, Dr. {doc['full_name']}! 🏥\n\nYou have {len(apts)} appointments scheduled for today ({today_str}):\n\n"
                for a in apts:
                    pat = await phi_db.patients.find_one({"_id": a["patient_id"]})
                    time_str = a["appointment_datetime"].split(" ")[1]
                    summary += f"• {time_str}: {pat['full_name']} ({a['appointment_type']})\n"
                
                summary += "\nHave a great day!"
                await whatsapp_service.send_custom_message(doc["whatsapp_number"], summary)
                logger.info(f"[AUTOMATION] Sent daily briefing to Dr. {doc['full_name']}")
                
        except Exception as e:
            logger.error(f"[AUTOMATION ERROR] Briefing: {e}")

    async def run_upcoming_alerts(self):
        """Checks for appointments happening in exactly 1 hour and alerts both doctor and patient."""
        profile_db = get_profile_db()
        phi_db = get_phi_db()
        
        try:
            one_hour_later = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            # This is a simple string match for demonstration; robust systems use datetime objects
            apts = await phi_db.appointments.find({
                "appointment_datetime": {"$regex": f"^{one_hour_later}"},
                "status": "scheduled",
                "reminder_sent": {"$ne": True}
            }).to_list(length=100)
            
            for a in apts:
                pat = await phi_db.patients.find_one({"_id": a["patient_id"]})
                doc = await profile_db.doctors.find_one({"_id": a["doctor_id"]})
                
                if pat and pat.get("phone_number"):
                    pat_msg = f"Hi {pat['full_name']}, just a reminder that your appointment with Dr. {doc['full_name']} is in 1 hour (at {a['appointment_datetime'].split(' ')[1]}). See you soon! 🏥"
                    await whatsapp_service.send_custom_message(pat["phone_number"], pat_msg)
                
                if doc and doc.get("whatsapp_number"):
                    doc_msg = f"Dr. {doc['full_name']}, your next patient {pat['full_name']} is scheduled in 1 hour. \n\nComplaint: {a.get('chief_complaint', 'N/A')}\nStatus: {'OLD_PATIENT' if pat.get('created_at') < datetime.utcnow() - timedelta(days=1) else 'NEW_PATIENT'}"
                    await whatsapp_service.send_custom_message(doc["whatsapp_number"], doc_msg)
                
                # Mark as sent
                await phi_db.appointments.update_one({"_id": a["_id"]}, {"$set": {"reminder_sent": True}})
                logger.info(f"[AUTOMATION] Sent 1-hour alerts for appointment {a.get('appointment_uuid')}")

        except Exception as e:
            logger.error(f"[AUTOMATION ERROR] Alerts: {e}")

automation_service = AutomationService()
