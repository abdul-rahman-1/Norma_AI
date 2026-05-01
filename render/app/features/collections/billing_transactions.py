import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "transaction_type", "amount", "status", "patient_id", "appointment_id", "timestamp" }

async def handle_billing_transactions(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "CREATE":
            params["timestamp"] = datetime.utcnow()
            await db.billing_transactions.insert_one(params)
            return {"status": "success"}
        elif op_type == "LIST":
            res = await db.billing_transactions.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
    except Exception as e:
        return {"error": str(e)}
