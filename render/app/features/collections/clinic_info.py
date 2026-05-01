import json
from datetime import datetime
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "clinic_uuid", "clinic_name", "clinic_type", "license_number", "email", "phone", "whatsapp_number", "address", "city", "country", "timezone", "currency", "website", "logo_url", "specialties", "services_offered", "languages_spoken", "subscription_plan", "subscription_status", "created_at", "updated_at" }

async def handle_clinic_info(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "GET":
            res = await db.clinic_info.find_one(params)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "UPDATE":
            params["updated_at"] = datetime.utcnow()
            await db.clinic_info.update_one({}, {"$set": params}, upsert=True)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
