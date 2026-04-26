import asyncio
from datetime import datetime, timedelta
from app.db.mongodb import get_phi_db, get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.logger import logger
import json

class AutomationService:
    async def send_doctor_daily_briefing(self):
        """Sends a high-level summary of the day's roster to all active doctors."""
        profile_db = get_profile_db()
        phi_db = get_phi_db()
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            doctors = await profile_db.doctors.find({"is_active": True}).to_list(length=50)
            for doc in doctors:
                if not doc.get("whatsapp_number"): continue
                apts = await phi_db.appointments.find({"doctor_id": doc["_id"], "appointment_datetime": {"$regex": f"^{today}"}}).to_list(length=50)
                if not apts: continue
                msg = f"🏥 *Daily Briefing: Dr. {doc['full_name']}*\n\nYou have {len(apts)} appointments today.\n\n"
                for a in apts:
                    p = await phi_db.patients.find_one({"_id": a["patient_id"]})
                    time = a["appointment_datetime"].split(" ")[1]
                    msg += f"• {time}: {p['full_name']} ({a['appointment_type']})\n"
                await whatsapp_service.send_custom_message(doc["whatsapp_number"], msg)
        except Exception as e:
            logger.error(f"BRIEFING_ERROR: {e}")

    async def run_proactive_alerts(self):
        """1-hour reminders and medical record prep for doctors."""
        phi_db = get_phi_db()
        profile_db = get_profile_db()
        try:
            target_time = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            apts = await phi_db.appointments.find({"appointment_datetime": {"$regex": f"^{target_time}"}, "status": "scheduled", "reminder_sent": {"$ne": True}}).to_list(length=20)
            for a in apts:
                p = await phi_db.patients.find_one({"_id": a["patient_id"]})
                d = await profile_db.doctors.find_one({"_id": a["doctor_id"]})
                # Alert Patient
                await whatsapp_service.send_custom_message(p["phone_number"], f"Hi {p['full_name']}, your appointment with Dr. {d['full_name']} is in 1 hour. See you soon!")
                # Alert Doctor with clinical context
                doc_msg = f"🔔 *Next Patient Context*\nPatient: {p['full_name']}\nReason: {a.get('chief_complaint')}\nAlerts: {p.get('medical_alerts', 'None')}"
                await whatsapp_service.send_custom_message(d["whatsapp_number"], doc_msg)
                await phi_db.appointments.update_one({"_id": a["_id"]}, {"$set": {"reminder_sent": True}})
        except Exception as e:
            logger.error(f"ALERT_ERROR: {e}")

automation_service = AutomationService()
