import json
from datetime import datetime
from app.db.mongodb import get_phi_db
from app.utils.data_formatter import format_patient

# SCHEMA: { "id", "patient_uuid", "full_name", "phone_number", "email", "date_of_birth", "gender", "address", "emergency_contact_name", "emergency_contact_phone", "preferred_language", "first_visit_date", "last_visit_date", "total_visits", "medical_alerts", "insurance_provider", "insurance_id", "notes", "created_at", "updated_at", "created_by", "is_active" }

from bson import ObjectId

async def handle_patients(op_type, params, user_data=None):
    db = get_phi_db()
    try:
        # Robust ObjectId conversion for filters
        processed_params = {}
        for k, v in params.items():
            if isinstance(v, str) and ObjectId.is_valid(v):
                processed_params[k] = ObjectId(v)
            else:
                processed_params[k] = v

        if op_type == "GET":
            res = await db.patients.find_one(processed_params)
            if not res:
                return {"error": "Patient not found."}
            
            # Format for user display
            raw_data = json.loads(json.dumps(res, default=str))
            formatted_output = format_patient(raw_data)
            return {"formatted": formatted_output, "raw": raw_data}
        
        elif op_type == "CREATE":
            params["created_at"] = datetime.utcnow()
            params["updated_at"] = datetime.utcnow()
            params["is_active"] = True
            await db.patients.insert_one(params)
            return {"status": "success", "message": "Patient record created."}

        elif op_type == "UPDATE":
            # Identify by _id, patient_uuid, or phone_number
            query = {}
            if "_id" in params: query["_id"] = params.pop("_id")
            elif "patient_uuid" in params: query["patient_uuid"] = params.pop("patient_uuid")
            elif "phone_number" in params: query["phone_number"] = params.pop("phone_number")
            
            if not query: return {"error": "Missing identifier for update."}
            
            params["updated_at"] = datetime.utcnow()
            await db.patients.update_one(query, {"$set": params})
            return {"status": "success", "message": "Profile updated successfully."}
    except Exception as e:
        return {"error": str(e)}
