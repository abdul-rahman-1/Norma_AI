import json
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "integration_type", "system_name", "api_key", "status", "last_sync" }

async def handle_system_integrations(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "GET":
            res = await db.system_integrations.find_one(params)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "LIST":
            res = await db.system_integrations.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
