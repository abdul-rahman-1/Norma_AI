import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "record_uuid", "patient_id", "appointment_id", "record_date", "record_type", "title", "content", "structured_data", "attachments", "doctor_id", "created_at", "created_by" }

async def handle_medical_records(op_type, params, user_data=None):
    db = get_phi_db()
    try:
        if op_type == "LIST":
            res = await db.medical_records.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
