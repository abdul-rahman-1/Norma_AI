import json
from app.db.mongodb import get_profile_db

# SCHEMA: { "id", "template_uuid", "category", "text_en", "created_at", "updated_at" }

async def handle_response_templates(op_type, params):
    db = get_profile_db()
    try:
        if op_type == "GET":
            res = await db.response_templates.find_one(params)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "LIST":
            res = await db.response_templates.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
