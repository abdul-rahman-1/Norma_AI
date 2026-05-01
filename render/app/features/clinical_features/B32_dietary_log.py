import json
from datetime import datetime
from app.db.mongodb import get_phi_db

async def execute_dietary_log(params, user_role, user_data=None):
    """Action B32: Log food photos/descriptions to medical records."""
    phi_db = get_phi_db()
    
    log_entry = {
        "record_uuid": params.get("media_id"),
        "patient_id": user_data["_id"],
        "record_type": "DIETARY_LOG",
        "title": "Dietary Update",
        "content": params.get("description", "Food photo uploaded."),
        "structured_data": {"calories_est": params.get("calories")},
        "created_at": datetime.utcnow()
    }
    
    await phi_db.medical_records.insert_one(log_entry)
    return {"status": "success", "message": "Dietary log saved."}
