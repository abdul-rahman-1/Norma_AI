import json
from app.db.mongodb import get_phi_db

# COLLECTIONS: activity_log, notifications, billing_transactions, analytics_snapshots, response_templates

async def handle_system_ops(collection_name, op_type, params):
    db = get_phi_db()
    try:
        if op_type == "LIST":
            res = await db[collection_name].find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "LOG":
            await db[collection_name].insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
