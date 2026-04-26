import json
import uuid
from datetime import datetime
from app.db.mongodb import get_phi_db, get_profile_db

async def execute_registration(op_type, params, user_role, sender_phone):
    phi_db = get_phi_db()
    profile_db = get_profile_db()

    try:
        if op_type == "REGISTER_PATIENT":
            # Permitted for Staff or New User (Self-Serve)
            new_patient = {
                "patient_uuid": str(uuid.uuid4()),
                "full_name": params['full_name'],
                "phone_number": sender_phone if user_role == "NEW_PATIENT" else params.get('phone'),
                "created_at": datetime.utcnow()
            }
            await phi_db.patients.update_one({"phone_number": new_patient["phone_number"]}, {"$set": new_patient}, upsert=True)
            return {"status": "success", "message": f"Patient {params['full_name']} registered."}

        elif op_type == "REGISTER_STAFF":
            # Permitted for Doctors and Admins
            if user_role not in ["DOCTOR", "ADMIN"]:
                return {"error": "Only Doctors or Admins can register Staff members."}
            
            new_staff = {
                "user_uuid": str(uuid.uuid4()),
                "full_name": params['full_name'],
                "phone": params['phone'],
                "role": "STAFF"
            }
            await profile_db.staff_users.insert_one(new_staff)
            return {"status": "success", "message": f"Staff member {params['full_name']} authorized."}

        elif op_type == "REGISTER_DOCTOR":
            # Permitted ONLY for Admins
            if user_role != "ADMIN":
                return {"error": "Only the System Admin can register new Doctors."}
            
            new_doctor = {
                "doctor_uuid": str(uuid.uuid4()),
                "full_name": params['full_name'],
                "whatsapp_number": params['phone'],
                "is_active": True
            }
            await profile_db.doctors.insert_one(new_doctor)
            return {"status": "success", "message": f"Dr. {params['full_name']} onboarded."}

        return {"status": "error", "message": "Unknown registration type."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
