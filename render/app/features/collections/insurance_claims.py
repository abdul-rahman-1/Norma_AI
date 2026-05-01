import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "claim_uuid", "patient_id", "appointment_id", "insurance_provider", "policy_number", "claim_amount", "approved_amount", "claim_status", "claim_date", "approval_date", "rejection_reason", "tpa_reference", "documents", "created_at", "updated_at" }

async def handle_insurance_claims(op_type, params):
    db = get_phi_db()
    try:
        if op_type == "LIST":
            res = await db.insurance_claims.find(params).to_list(length=100)
            return json.loads(json.dumps(res, default=str))
        elif op_type == "CREATE":
            params["created_at"] = datetime.utcnow()
            await db.insurance_claims.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
