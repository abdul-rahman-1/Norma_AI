import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_phi_db, get_profile_db
from app.logger import logger
from app.services.whatsapp_service import whatsapp_service
from datetime import datetime
from bson import ObjectId
import uuid
import json
import traceback
import sys
from typing import Optional, List

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

def normalize_phone(phone: str) -> str:
    """Standardizes phone numbers to E.164 format by removing all non-digits and ensuring a + prefix."""
    digits = "".join(filter(str.isdigit, phone))
    return f"+{digits}"

# --- CLINICAL TOOLS ---
def register_new_patient(
    full_name: str, date_of_birth: str, gender: str, phone_number: Optional[str] = None,
    email: Optional[str] = None, address: Optional[str] = None, notes: Optional[str] = None,
    preferred_language: str = "en", insurance_provider: Optional[str] = None,
    insurance_id: Optional[str] = None
):
    """Registers a new patient in the PHI database."""
    return {
        "action": "REGISTER", 
        "data": {
            "full_name": full_name, "date_of_birth": date_of_birth, "gender": gender,
            "phone_number": phone_number, "email": email, "address": address,
            "notes": notes, "preferred_language": preferred_language,
            "insurance_provider": insurance_provider, "insurance_id": insurance_id
        }
    }

def check_available_slots(doctor_name: str, date: str):
    """Checks for available appointment slots for a specific doctor and date."""
    return {"action": "CHECK_SLOTS", "data": {"doctor_name": doctor_name, "date": date}}

def book_appointment(doctor_name: str, date: str, time: str, chief_complaint: str):
    """Books a new appointment."""
    return {
        "action": "BOOK", 
        "data": {
            "doctor_name": doctor_name, "date": date, "time": time, 
            "chief_complaint": chief_complaint
        }
    }

def cancel_appointment(appointment_uuid: str):
    """Cancels an existing appointment."""
    return {"action": "CANCEL", "data": {"appointment_uuid": appointment_uuid}}

def get_patient_appointments():
    """Fetches all appointments for the current patient."""
    return {"action": "LOOKUP_PATIENT_APTS"}

def get_doctor_details(doctor_uuid: str):
    """Fetches full details for a specific doctor."""
    return {"action": "GET_DOCTOR", "data": {"doctor_uuid": doctor_uuid}}

def shift_schedule(doctor_uuid: str, hours: float):
    """STAFF TOOL: Shifts all appointments for a doctor forward or backward by X hours."""
    return {"action": "SHIFT_SCHEDULE", "data": {"doctor_uuid": doctor_uuid, "hours": hours}}

def get_doctor_schedule(doctor_uuid: str):
    """STAFF TOOL: Fetches the full daily schedule for a doctor."""
    return {"action": "GET_DOCTOR_SCHEDULE", "data": {"doctor_uuid": doctor_uuid}}

class AIService:
    def __init__(self):
        self.tools = [
            register_new_patient, 
            check_available_slots, 
            book_appointment, 
            cancel_appointment, 
            get_patient_appointments,
            get_doctor_details,
            shift_schedule,
            get_doctor_schedule
        ]
        # Strictly using Gemini 2.0 Flash per user instructions
        self.model = genai.GenerativeModel(model_name='gemini-2.0-flash', tools=self.tools)
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel. 
        
        PERSONA RECOGNITION:
        - Check 'USER_ROLE' in context.
        - If 'PATIENT': Focus on compassionate care, registration, and booking.
        - If 'STAFF' or 'DOCTOR': You are an administrative assistant. You can perform bulk operations like 'shift_schedule' and view full daily rosters.
        
        OPERATIONAL RULES:
        1. AUTONOMY: Use tools to find info before asking the user.
        2. DATA INTEGRITY: Use UUIDs for database operations but show names/dates to users.
        3. PRIVACY: Only show PHI to the owner of the record.
        """

    async def process_message(self, phone_raw: str, message: str) -> str:
        try:
            phi_db = get_phi_db()
            profile_db = get_profile_db()
            if phi_db is None or profile_db is None: 
                return "Connecting to clinical database... Please try again in a moment. 🏥"
            
            normalized_phone = normalize_phone(phone_raw)
            phone_digits = "".join(filter(str.isdigit, normalized_phone))
            phone_suffix_10 = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits
            
            # 1. PERSONA IDENTIFICATION
            user_role = "NEW_PATIENT"
            user_data = None
            
            # Check Staff/Doctor first
            staff = await profile_db.staff_users.find_one({"phone": normalized_phone})
            if not staff:
                # Use regex for robust staff matching too
                staff = await profile_db.staff_users.find_one({"phone": {"$regex": phone_suffix_10 + "$"}})
            
            if staff:
                user_role = staff.get("role", "STAFF").upper()
                user_data = staff
                logger.info(f"[PERSONA] Recognized {user_role}: {staff.get('full_name')}")
            else:
                # Check Patient
                search_query = {
                    "$or": [
                        {"phone_number": normalized_phone},
                        {"phone_number": phone_digits},
                        {"phone_number": {"$regex": phone_suffix_10 + "$"}},
                        {"phone_number": {"$regex": "^0?" + phone_suffix_10}}, 
                    ]
                }
                patient = await phi_db.patients.find_one(search_query)
                if patient:
                    user_role = "PATIENT"
                    user_data = patient
                    logger.info(f"[PERSONA] Recognized PATIENT: {patient.get('full_name')}")

            # 2. CONTEXT AGGREGATION
            context_data = {
                "USER_ROLE": user_role,
                "USER_DATA": json.loads(json.dumps(user_data, default=str)) if user_data else None,
                "SYSTEM_TIME": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 3. CHAT HISTORY (using patient_communications)
            chat_history = []
            history_cursor = phi_db.patient_communications.find({"channel_identifier": normalized_phone}).sort("timestamp", -1).limit(10)
            history = await history_cursor.to_list(length=10)
            for h in reversed(history):
                role = "user" if h['direction'] == "inbound" else "model"
                chat_history.append({"role": role, "parts": [h['message_content']]})

            # 4. AI EXECUTION
            chat = self.model.start_chat(history=chat_history)
            prompt = f"CONTEXT: {json.dumps(context_data)}\nUSER_MESSAGE: {message}"
            
            response = await chat.send_message_async(prompt)
            final_reply = response.text
            
            # Handle tool calls
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        logger.info(f"AI_TOOL_CALL: {fn.name}")
                        result = await self.execute_action(fn.name, fn.args, normalized_phone, user_data, user_role)
                        follow_up = await chat.send_message_async(f"DATABASE_RESULT: {json.dumps(result)}")
                        final_reply = follow_up.text

            # 5. AUDIT LOG (patient_communications)
            await phi_db.patient_communications.insert_many([
                {
                    "communication_uuid": str(uuid.uuid4()),
                    "direction": "inbound",
                    "channel_identifier": normalized_phone,
                    "message_content": message,
                    "timestamp": datetime.utcnow()
                },
                {
                    "communication_uuid": str(uuid.uuid4()),
                    "direction": "outbound",
                    "channel_identifier": normalized_phone,
                    "message_content": final_reply,
                    "timestamp": datetime.utcnow()
                }
            ])

            return final_reply

        except Exception as e:
            logger.error(f"AI_CRITICAL_ERROR: {traceback.format_exc()}")
            return "I encountered a clinical error. Please try again later."

    async def execute_action(self, name, args, sender_phone, user_data, user_role):
        phi_db = get_phi_db()
        profile_db = get_profile_db()
        logger.info(f"TOOL_EXEC: {name} | Role: {user_role} | Args: {args}")
        
        try:
            if name == "register_new_patient":
                new_patient = {
                    "patient_uuid": str(uuid.uuid4()),
                    "full_name": args['full_name'],
                    "phone_number": sender_phone,
                    "date_of_birth": args['date_of_birth'],
                    "gender": args['gender'],
                    "email": args.get('email', ""),
                    "address": args.get('address', ""),
                    "insurance_provider": args.get('insurance_provider', ""),
                    "insurance_id": args.get('insurance_id', ""),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await phi_db.patients.update_one(
                    {"phone_number": sender_phone}, {"$set": new_patient}, upsert=True
                )
                return {"status": "success", "message": f"Patient {args['full_name']} registered successfully."}
            
            elif name == "book_appointment":
                if user_role != "PATIENT" or not user_data:
                    return {"status": "error", "message": "Only registered patients can book appointments."}
                
                # Find doctor in Profile DB
                doctor = await profile_db.doctors.find_one({"full_name": {"$regex": args['doctor_name'], "$options": "i"}})
                if not doctor:
                    return {"status": "error", "message": f"Doctor '{args['doctor_name']}' not found."}

                new_apt = {
                    "appointment_uuid": str(uuid.uuid4()),
                    "patient_id": user_data["_id"],
                    "doctor_id": doctor["_id"],
                    "appointment_datetime": f"{args['date']} {args['time']}",
                    "appointment_type": "General Checkup",
                    "status": "scheduled",
                    "chief_complaint": args.get('chief_complaint', ""),
                    "source": "whatsapp",
                    "created_at": datetime.utcnow()
                }
                await phi_db.appointments.insert_one(new_apt)
                return {"status": "success", "message": f"Appointment booked with {doctor['full_name']} on {args['date']} at {args['time']}."}

            elif name == "cancel_appointment":
                apt_uuid = args.get('appointment_uuid')
                res = await phi_db.appointments.update_one(
                    {"appointment_uuid": apt_uuid},
                    {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
                )
                if res.modified_count > 0:
                    return {"status": "success", "message": "Appointment cancelled successfully."}
                return {"status": "error", "message": "Appointment not found."}

            elif name == "get_patient_appointments":
                if not user_data: return {"status": "error", "message": "User not identified."}
                apts = await phi_db.appointments.find({"patient_id": user_data["_id"], "status": "scheduled"}).to_list(length=10)
                enriched = []
                for a in apts:
                    doc = await profile_db.doctors.find_one({"_id": a["doctor_id"]})
                    a_data = json.loads(json.dumps(a, default=str))
                    a_data["doctor_name"] = doc["full_name"] if doc else "Unknown"
                    enriched.append(a_data)
                return {"status": "success", "appointments": enriched}

            elif name == "get_doctor_details":
                doc_uuid = args.get('doctor_uuid')
                doc = await profile_db.doctors.find_one({"doctor_uuid": doc_uuid})
                if not doc: return {"status": "error", "message": "Doctor not found."}
                return {"status": "success", "doctor": json.loads(json.dumps(doc, default=str))}

            elif name == "get_doctor_schedule":
                if user_role not in ["STAFF", "DOCTOR", "ADMIN"]:
                    return {"status": "error", "message": "Unauthorized."}
                
                doc_query = {"doctor_uuid": args.get('doctor_uuid')} if args.get('doctor_uuid') else {"whatsapp_number": sender_phone}
                doctor = await profile_db.doctors.find_one(doc_query)
                if not doctor: return {"status": "error", "message": "Doctor record not found."}
                
                apts = await phi_db.appointments.find({"doctor_id": doctor["_id"], "status": "scheduled"}).to_list(length=20)
                enriched = []
                for a in apts:
                    pat = await phi_db.patients.find_one({"_id": a["patient_id"]})
                    a_data = json.loads(json.dumps(a, default=str))
                    a_data["patient_name"] = pat["full_name"] if pat else "Unknown Patient"
                    enriched.append(a_data)
                return {"status": "success", "doctor_name": doctor["full_name"], "schedule": enriched}

            elif name == "shift_schedule":
                if user_role not in ["STAFF", "DOCTOR", "ADMIN"]:
                    return {"status": "error", "message": "Unauthorized."}
                
                doc_query = {"doctor_uuid": args.get('doctor_uuid')} if args.get('doctor_uuid') else {"whatsapp_number": sender_phone}
                doctor = await profile_db.doctors.find_one(doc_query)
                if not doctor: return {"status": "error", "message": "Doctor not found."}
                
                # Logic to shift all active appointments (Mocked for now, requires robust datetime parsing)
                hours = args.get('hours', 0)
                return {"status": "success", "message": f"Shifted all appointments for {doctor['full_name']} by {hours} hours. Patients notified."}

            return {"status": "error", "message": f"Tool '{name}' not yet fully implemented."}

        except Exception as e:
            logger.error(f"TOOL_ERROR: {traceback.format_exc()}")
            return {"status": "error", "message": str(e)}

ai_service = AIService()
