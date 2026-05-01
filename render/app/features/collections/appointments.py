import json
from datetime import datetime
from app.db.mongodb import get_phi_db
from bson import ObjectId
from app.utils.data_formatter import format_appointments_list

# SCHEMA: { "id", "appointment_uuid", "patient_id", "doctor_id", "appointment_datetime", "duration_minutes", "appointment_type", "status", "cancellation_reason", "chief_complaint", "diagnosis", "treatment_plan", "prescription", "lab_orders", "follow_up_required", "follow_up_date", "notes", "reminder_sent", "reminder_sent_at", "confirmed_by_patient", "confirmed_at", "source", "created_at", "updated_at", "created_by" }

async def handle_appointments(op_type, params, user_data=None):
    db = get_phi_db()
    try:
        # Robust ObjectId conversion for filters
        processed_params = {}
        for k, v in params.items():
            if isinstance(v, str) and ObjectId.is_valid(v):
                processed_params[k] = ObjectId(v)
            else:
                processed_params[k] = v

        if op_type == "LIST":
            # ENHANCED: Use aggregate to join BOTH patient AND doctor details
            pipeline = [
                {"$match": processed_params},
                {
                    "$lookup": {
                        "from": "patients",
                        "localField": "patient_id",
                        "foreignField": "_id",
                        "as": "patient"
                    }
                },
                {"$unwind": {"path": "$patient", "preserveNullAndEmptyArrays": True}},
                {
                    "$lookup": {
                        "from": "doctors",
                        "localField": "doctor_id",
                        "foreignField": "_id",
                        "as": "doctor"
                    }
                },
                {"$unwind": {"path": "$doctor", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "appointment_datetime": 1,
                        "status": 1,
                        "appointment_type": 1,
                        "patient_name": "$patient.full_name",
                        "patient_phone": "$patient.phone_number",
                        "doctor_name": "$doctor.full_name",
                        "doctor_id": 1
                    }
                },
                {"$sort": {"appointment_datetime": 1}}
            ]
            
            res = await db.appointments.aggregate(pipeline).to_list(length=50)
            raw_data = json.loads(json.dumps(res, default=str))
            
            # Format for user-facing output (hide IDs, format dates)
            formatted_output = format_appointments_list(raw_data)
            return {"formatted": formatted_output, "raw": raw_data}

        elif op_type == "CREATE":
            params["created_at"] = datetime.utcnow()
            await db.appointments.insert_one(params)
            return {"status": "success"}
            
        elif op_type == "UPDATE":
            apt_id = params.pop("_id", None) or params.pop("appointment_id", None)
            if not apt_id: return {"error": "Missing appointment identifier."}
            
            await db.appointments.update_one({"_id": ObjectId(apt_id)}, {"$set": params})
            return {"status": "success", "message": "Appointment updated."}

    except Exception as e:
        import traceback
        print(f"APPOINTMENT_HANDLE_ERROR: {traceback.format_exc()}")
        return {"error": str(e)}
