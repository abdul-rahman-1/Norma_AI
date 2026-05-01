import json
from datetime import datetime
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "identifier", "username", "password_hash", "role", "name", "created_at", "updated_at" }

async def handle_login_details(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "GET":
            res = await db.login_details.find_one(params)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "CREATE":
            params["created_at"] = datetime.utcnow()
            params["updated_at"] = datetime.utcnow()
            await db.login_details.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
