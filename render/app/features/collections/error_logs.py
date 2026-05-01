import json
from datetime import datetime
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "error_message", "stack_trace", "timestamp", "user_id" }

async def handle_error_logs(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "LOG":
            params["timestamp"] = datetime.utcnow()
            await db.error_logs.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
