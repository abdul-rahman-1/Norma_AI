import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "total_appointments", "revenue_generated", "snapshot_date" }

async def handle_analytics_snapshots(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "LIST":
            res = await db.analytics_snapshots.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "CREATE":
            params["snapshot_date"] = datetime.utcnow()
            await db.analytics_snapshots.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
