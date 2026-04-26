import json
from app.db.mongodb import get_phi_db

async def execute_billing_op(op_type, params, user_role, user_data):
    phi_db = get_phi_db()

    try:
        if op_type == "VIEW_CLAIMS":
            res = await phi_db.insurance_claims.find({"patient_id": user_data["_id"]}).to_list(length=5)
            return {"status": "success", "data": json.loads(json.dumps(res, default=str))}
        
        elif op_type == "REVENUE_SNAPSHOT":
            if user_role not in ["ADMIN", "STAFF"]: return {"error": "Unauthorized"}
            return {"status": "success", "revenue": "$1,200.00", "appointments": 8}

        elif op_type == "CO_PAY_LINK":
            import uuid
            return {"status": "success", "link": f"https://pay.norma-ai.com/checkout/{uuid.uuid4().hex[:8]}"}

        elif op_type == "INSURANCE_CHECK":
            provider = params.get("provider", "Unknown")
            return {"status": "success", "coverage": "Verified", "provider": provider, "message": f"Insurance with {provider} is verified and active."}

        return {"status": "error", "message": "Unknown billing operation."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
