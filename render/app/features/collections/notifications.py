import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "notification_type", "message", "patient_id", "status", "timestamp" }

async def handle_notifications(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "SEND":
            params["timestamp"] = datetime.utcnow()
            params["status"] = "sent"
            await db.notifications.insert_one(params)
            return {"status": "success"}
        elif op_type == "LIST":
            res = await db.notifications.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
