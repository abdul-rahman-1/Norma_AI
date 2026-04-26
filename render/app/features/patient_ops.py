import json
from datetime import datetime
import uuid
from app.db.mongodb import get_phi_db, get_profile_db
from app.logger import logger

async def execute_patient_op(op_type, params, user_data):
    if not user_data or "_id" not in user_data:
        return {"status": "error", "message": "Patient record not found. Please register first."}

    phi_db = get_phi_db()
    
    # RBAC: Force user identity
    params["patient_id"] = user_data["_id"]

    try:
        if op_type == "FETCH_HISTORY":
            res = await phi_db.appointments.find({"patient_id": user_data["_id"]}).to_list(length=10)
            return {"status": "success", "data": json.loads(json.dumps(res, default=str))}
        
        elif op_type == "VIEW_RECORDS":
            res = await phi_db.medical_records.find({"patient_id": user_data["_id"]}).to_list(length=10)
            return {"status": "success", "data": json.loads(json.dumps(res, default=str))}

        elif op_type == "BOOK_TELEHEALTH":
            return {"status": "success", "link": f"https://zoom.us/j/{uuid.uuid4().hex[:10]}", "note": "Virtual link generated."}

        elif op_type == "BOOK_APPOINTMENT":
            appointment = {
                "patient_id": user_data["_id"],
                "doctor_id": params.get("doctor_id", "unassigned"),
                "appointment_datetime": params.get("datetime", datetime.utcnow().strftime("%Y-%m-%d %H:%M")),
                "status": "scheduled",
                "appointment_type": params.get("type", "General Consultation")
            }
            await phi_db.appointments.insert_one(appointment)
            return {"status": "success", "message": f"Appointment booked for {appointment['appointment_datetime']}."}

        elif op_type == "RESCHEDULE_APPOINTMENT":
            # For simplicity, finding latest and updating
            res = await phi_db.appointments.update_one(
                {"patient_id": user_data["_id"], "status": "scheduled"},
                {"$set": {"appointment_datetime": params.get("new_datetime")}}
            )
            if res.modified_count > 0:
                return {"status": "success", "message": "Appointment rescheduled."}
            return {"status": "error", "message": "No active appointment found."}

        elif op_type == "CANCEL_APPOINTMENT":
            res = await phi_db.appointments.update_one(
                {"patient_id": user_data["_id"], "status": "scheduled"},
                {"$set": {"status": "cancelled"}}
            )
            if res.modified_count > 0:
                return {"status": "success", "message": "Appointment cancelled."}
            return {"status": "error", "message": "No active appointment found."}

        elif op_type == "PORTAL_LINK":
            return {"status": "success", "link": f"https://portal.norma-ai.com/auth/{uuid.uuid4().hex[:8]}"}

        return {"status": "error", "message": f"Patient operation {op_type} not found."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
