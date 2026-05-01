import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "prescription_uuid", "patient_id", "appointment_id", "doctor_id", "prescription_date", "medications", "pharmacy_name", "pharmacy_phone", "filled_status", "filled_date", "refill_allowed", "refill_count", "notes", "created_at" }

async def handle_prescriptions(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "LIST":
            res = await db.prescriptions.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "CREATE":
            params["created_at"] = datetime.utcnow()
            await db.prescriptions.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
