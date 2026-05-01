import json
from datetime import datetime
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "doctor_uuid", "full_name", "specialty", "license_number", "whatsapp_number", "email", "phone", "consultation_fee", "bio", "photo_url", "google_calendar_id", "is_active", "created_at", "updated_at" }

async def handle_doctors(op_type, params, user_data=None):
    db = get_profile_db()
    try:
        if op_type == "LIST":
            res = await db.doctors.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
