import json
from app.db.mongodb import get_phi_db
from app.services.whatsapp_service import whatsapp_service

async def execute_cancel_and_fill(params, user_role, user_data=None):
    """Action B33: Auto-book waitlisted patients when a slot opens."""
    phi_db = get_phi_db()
    doctor_id = params.get("doctor_id")
    date = params.get("date")

    # Find next patient in waitlist
    next_up = await phi_db.activity_log.find_one({"action_type": "WAITLIST", "status": "pending"}, sort=[("timestamp", 1)])
    
    if next_up:
        # Notify waitlisted patient
        patient = await phi_db.patients.find_one({"_id": next_up["patient_id"]})
        if patient:
            msg = f"✨ *Great News*\nA slot just opened up for Dr. Smith. Would you like to book it?"
            await whatsapp_service.send_custom_message(patient["phone_number"], msg)
            return {"status": "success", "message": "Waitlisted patient notified."}
    return {"status": "success", "message": "No waitlist to fill."}
