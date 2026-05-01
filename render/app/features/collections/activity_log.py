import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "action_type", "entity_type", "description", "user_id", "timestamp" }

async def handle_activity_log(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "LOG":
            params["timestamp"] = datetime.utcnow()
            await db.activity_log.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
