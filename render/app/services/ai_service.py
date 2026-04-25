import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_db
from app.logger import logger
from app.services.whatsapp_service import whatsapp_service
from datetime import datetime
import uuid
import json
import traceback
import sys
from typing import Optional, List

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

def flush_print(msg):
    print(msg)
    sys.stdout.flush()

def normalize_phone(phone: str) -> str:
    """Standardizes phone numbers to the last 10 digits."""
    return "".join(filter(str.isdigit, phone))[-10:]

# --- CLINICAL TOOLS ---
def register_new_patient(
    full_name: str, date_of_birth: str, gender: str, phone_number: Optional[str] = None,
    email: Optional[str] = None, address: Optional[str] = None, emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None, preferred_language: str = "ar",
    medical_alerts: Optional[List[str]] = None, insurance_provider: Optional[str] = None,
    insurance_id: Optional[str] = None, notes: Optional[str] = None
):
    return {
        "action": "REGISTER", 
        "data": {
            "full_name": full_name, "date_of_birth": date_of_birth, "gender": gender,
            "phone_number": phone_number, "email": email, "address": address,
            "emergency_contact_name": emergency_contact_name, "emergency_contact_phone": emergency_contact_phone,
            "preferred_language": preferred_language, "medical_alerts": medical_alerts,
            "insurance_provider": insurance_provider, "insurance_id": insurance_id, "notes": notes
        }
    }

def check_available_slots(doctor_name: str, date: str):
    return {"action": "CHECK_SLOTS", "data": {"doctor_name": doctor_name, "date": date}}

def book_appointment(doctor_name: str, date: str, time: str, chief_complaint: str, appointment_type: str = "consultation"):
    return {
        "action": "BOOK", 
        "data": {
            "doctor": doctor_name, "date": date, "time": time, 
            "chief_complaint": chief_complaint, "appointment_type": appointment_type
        }
    }

def cancel_appointment(appointment_id: Optional[str] = None):
    return {"action": "CANCEL", "data": {"appointment_id": appointment_id}}

def get_patient_appointments():
    return {"action": "LOOKUP"}

class AIService:
    def __init__(self):
        self.tools = [register_new_patient, check_available_slots, book_appointment, cancel_appointment, get_patient_appointments]
        # Always use gemini-2.5-flash as requested
        self.model = genai.GenerativeModel(model_name='gemini-2.5-flash', tools=self.tools)
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel. Your database is 'norma_ai'.
        
        ONBOARDING & CONTEXT LOGIC:
        - Check 'PATIENT_STATUS' in context.
        - If 'OLD_PATIENT': Greet with "Welcome back, [Name]! How can I help you today?"
        - If 'NEW_PATIENT': Greet with "Welcome to Norma AI! I'm here to help you register and book an appointment." 
          Then ask for all details sequentially: Full Name, DOB (YYYY-MM-DD), Gender, etc.
        """

    async def process_message(self, phone_raw: str, message: str) -> str:
        try:
            db = get_db()
            if db is None: return "DEBUG: Database connection is NULL. 🏥"
            
            phone_digits = "".join(filter(str.isdigit, phone_raw))
            phone_key_10 = phone_digits[-10:]
            flush_print(f"AI_PROCESS: RawPhone={phone_raw} Digits={phone_digits} Key10={phone_key_10}")
            
            # 1. HANDLE "CONFIRM"
            if message.strip().upper() == "CONFIRM":
                pending = await db.patients.find_one({
                    "$or": [{"phone": phone_key_10}, {"phone_number": {"$regex": phone_key_10}}],
                    "is_active": False
                })
                if pending:
                    await db.patients.update_one({"_id": pending["_id"]}, {"$set": {"is_active": True, "updated_at": datetime.utcnow()}})
                    return f"Thank you, {pending['full_name']}! Your registration on Norma-AI is confirmed."

            # 2. FETCH CONTEXT - ULTRA FLEXIBLE LOOKUP
            # Search for the 10-digit suffix in ANY likely field
            patient = await db.patients.find_one({
                "$or": [
                    {"phone": phone_key_10}, 
                    {"phone": {"$regex": phone_key_10}},
                    {"phone_number": phone_key_10},
                    {"phone_number": {"$regex": phone_key_10}},
                    {"phone": phone_digits},
                    {"phone_number": phone_digits}
                ]
            })
            
            status = "OLD_PATIENT" if patient else "NEW_PATIENT"
            flush_print(f"AI_STATUS: {status} (Found={bool(patient)})")
            if patient:
                flush_print(f"PATIENT_MATCH: Name='{patient.get('full_name')}' PhoneInDB='{patient.get('phone') or patient.get('phone_number')}'")
            
            # Fetch Context Data (Safe blocks)
            appointments = []
            try:
                apts_cursor = db.appointments.find({
                    "$or": [{"phone": phone_key_10}, {"patient_id": patient["_id"] if patient else None}]
                }).sort("appointment_datetime", 1)
                appointments = await apts_cursor.to_list(length=5)
                flush_print(f"DATA_FETCH: Found {len(appointments)} appointments")
            except: pass
            
            doctor_list = "None"
            try:
                docs = await db.doctors.find({"is_active": True}).to_list(length=10)
                doctor_list = "\n".join([f"- {d['full_name']} ({d['specialty']})" for d in docs])
                flush_print(f"DATA_FETCH: Found {len(docs)} doctors")
            except: pass

            chat_history = []
            try:
                history = await db.conversations.find({"phone": phone_key_10}).sort("timestamp", -1).limit(10).to_list(length=10)
                for h in reversed(history):
                    role = "user" if h['role'] == "user" else "model"
                    if not chat_history or chat_history[-1]["role"] != role:
                        chat_history.append({"role": role, "parts": [h['text']]})
                flush_print(f"DATA_FETCH: Loaded {len(chat_history)} history items")
            except: pass

            # 4. AI EXECUTION
            flush_print("AI_EXEC: Starting Gemini Chat session...")
            chat = self.model.start_chat(history=chat_history)
            prompt = f"PATIENT_STATUS: {status}\nPATIENT_DATA: {json.dumps(patient, default=str)}\nACTIVE_APPOINTMENTS: {json.dumps(appointments, default=str)}\nAVAILABLE_DOCTORS: {doctor_list}\nUSER_PHONE: {phone_key_10}\nUSER_MESSAGE: {message}"
            
            response = await chat.send_message_async(prompt)
            flush_print("AI_EXEC: Response received")
            
            final_reply = response.text
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        flush_print(f"AI_TOOL: Calling {fn.name}")
                        result = await self.execute_action(fn.name, fn.args, phone_key_10, patient)
                        follow_up = await chat.send_message_async(f"DATABASE_RESULT: {result}")
                        final_reply = follow_up.text

            try:
                await db.conversations.insert_many([
                    {"phone": phone_key_10, "role": "user", "text": message, "timestamp": datetime.utcnow()},
                    {"phone": phone_key_10, "role": "assistant", "text": final_reply, "timestamp": datetime.utcnow()}
                ])
                flush_print("AI_EXEC: Conversation saved")
            except: pass

            return final_reply

        except Exception as e:
            flush_print(f"AI_CRITICAL_ERROR: {traceback.format_exc()}")
            return f"DEBUG: SENTINEL ERROR - {str(e)} ⚠️"

    async def execute_action(self, name, args, sender_phone, patient):
        db = get_db()
        flush_print(f"TOOL_EXEC: {name}")
        try:
            if name == "register_new_patient":
                target_phone = normalize_phone(args.get('phone_number')) if args.get('phone_number') else sender_phone
                is_third_party = target_phone != sender_phone
                new_patient = {
                    "patient_uuid": str(uuid.uuid4()), "full_name": args['full_name'],
                    "phone": target_phone, "phone_number": target_phone,
                    "date_of_birth": args['date_of_birth'], "gender": args['gender'],
                    "is_active": not is_third_party, "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()
                }
                await db.patients.update_one({"phone": target_phone}, {"$set": new_patient}, upsert=True)
                if is_third_party:
                    await whatsapp_service.send_custom_message(args.get('phone_number'), f"u are being register on Norma-AI\nwrite confirm to register ur confirmation")
                    return "Confirmation request sent."
                return f"Welcome {args['full_name']}! Registration complete."
            
            elif name == "book_appointment":
                new_apt = {"appointment_uuid": str(uuid.uuid4()), "phone": sender_phone, "status": "scheduled", "chief_complaint": args['chief_complaint'], "created_at": datetime.utcnow()}
                await db.appointments.insert_one(new_apt)
                return "Appointment scheduled."
            
            return "Action executed."
        except Exception as e:
            flush_print(f"TOOL_ERROR: {e}")
            return f"Error executing {name}."

ai_service = AIService()
