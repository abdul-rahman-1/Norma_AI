import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "action", "resource_type", "status_code", "timestamp" }

async def handle_audit_log(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "LOG":
            params["timestamp"] = datetime.utcnow()
            await db.audit_log.insert_one(params)
            return {"status": "success"}
        elif op_type == "LIST":
            res = await db.audit_log.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
