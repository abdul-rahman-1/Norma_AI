from datetime import datetime, timedelta
from bson import ObjectId
from app.db.mongodb import get_phi_db, get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B24: Bulk Shift
    Move all appointments for a doctor by +1 day (or as specified).
    """
    allowed = ["DOCTOR", "ADMIN", "STAFF"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B24_BULK_SHIFT")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    phi_db = get_phi_db()
    profile_db = get_profile_db()
    try:
        doctor_id_raw = params.get("doctor_id") or (user_data["_id"] if user_role == "DOCTOR" else None)
        target_date = params.get("date") # Expected YYYY-MM-DD
        days_to_shift = params.get("days", 1)
        
        if not doctor_id_raw or not target_date:
            return {"status": "error", "message": "doctor_id and date are required for bulk shift."}

        d_id = ObjectId(doctor_id_raw) if ObjectId.is_valid(doctor_id_raw) else doctor_id_raw
        doctor = await profile_db.doctors.find_one({"_id": d_id})
        doc_name = doctor["full_name"] if doctor else "Doctor"

        # 1. Find all scheduled appointments for that doctor on that day
        query = {
            "doctor_id": d_id,
            "appointment_datetime": {"$regex": f"^{target_date}"},
            "status": "scheduled"
        }
        apts = await phi_db.appointments.find(query).to_list(length=100)
        
        if not apts:
            return {"status": "success", "message": f"No scheduled appointments found for {doc_name} on {target_date}."}

        shifted_count = 0
        for apt in apts:
            # 2. Calculate new date
            old_dt_str = apt["appointment_datetime"]
            dt_obj = datetime.strptime(old_dt_str, "%Y-%m-%d %H:%M")
            new_dt_obj = dt_obj + timedelta(days=days_to_shift)
            new_dt_str = new_dt_obj.strftime("%Y-%m-%d %H:%M")

            # 3. Update DB
            await phi_db.appointments.update_one(
                {"_id": apt["_id"]},
                {"$set": {"appointment_datetime": new_dt_str, "updated_at": datetime.utcnow()}}
            )

            # 4. NOTIFY PATIENT (MANDATORY)
            patient = await phi_db.patients.find_one({"_id": apt["patient_id"]})
            if patient and patient.get("phone_number"):
                msg = (
                    f"📢 *Clinical Schedule Update*\n"
                    f"Hi {patient['full_name']}, due to a change in {doc_name}'s schedule, "
                    f"your appointment has been rescheduled:\n\n"
                    f"🗓 *Old Time:* {old_dt_str}\n"
                    f"🗓 *New Time:* {new_dt_str}\n\n"
                    f"We apologize for the inconvenience."
                )
                await whatsapp_service.send_custom_message(patient["phone_number"], msg)
            
            shifted_count += 1

        return {
            "status": "success", 
            "message": f"Successfully shifted {shifted_count} appointments. All patients notified.",
            "shifted_count": shifted_count
        }

    except Exception as e:
        logger.error(f"B24_BULK_SHIFT_ERROR: {str(e)}")
        return {"status": "error", "message": f"Bulk shift failed: {str(e)}"}
