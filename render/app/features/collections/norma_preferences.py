import json
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "preference_key", "preference_value", "updated_at" }

async def handle_norma_preferences(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "GET":
            res = await db.norma_preferences.find_one({"preference_key": params["key"]})
            return json.loads(json.dumps(res, default=str))
        elif op_type == "UPDATE":
            from datetime import datetime
            await db.norma_preferences.update_one(
                {"preference_key": params["key"]},
                {"$set": {"preference_value": params["value"], "updated_at": datetime.utcnow()}},
                upsert=True
            )
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
