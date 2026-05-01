import json
from datetime import datetime
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "doctor_id", "day_of_week", "is_open", "open_time", "close_time", "break_start_time", "break_end_time", "notes", "effective_from", "effective_until", "created_at", "updated_at" }

async def handle_operating_hours(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "LIST":
            res = await db.operating_hours.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "UPDATE":
            query = {"doctor_id": params.pop("doctor_id"), "day_of_week": params.pop("day_of_week")}
            params["updated_at"] = datetime.utcnow()
            await db.operating_hours.update_one(query, {"$set": params}, upsert=True)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
