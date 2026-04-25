import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_db
from app.logger import logger
from app.services.whatsapp_service import whatsapp_service
from datetime import datetime
import uuid
import json
import traceback
from typing import Optional, List

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

def normalize_phone(phone: str) -> str:
    """Standardizes phone numbers to the last 10 digits."""
    return "".join(filter(str.isdigit, phone))[-10:]

# --- CLINICAL TOOLS ---
def register_new_patient(
    full_name: str, 
    date_of_birth: str, 
    gender: str, 
    phone_number: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    emergency_contact_name: Optional[str] = None,
    emergency_contact_phone: Optional[str] = None,
    preferred_language: str = "ar",
    medical_alerts: Optional[List[str]] = None,
    insurance_provider: Optional[str] = None,
    insurance_id: Optional[str] = None,
    notes: Optional[str] = None
):
    """Registers a new patient record in the norma_ai database."""
    return {
        "action": "REGISTER", 
        "data": {
            "full_name": full_name, 
            "date_of_birth": date_of_birth, 
            "gender": gender,
            "phone_number": phone_number,
            "email": email,
            "address": address,
            "emergency_contact_name": emergency_contact_name,
            "emergency_contact_phone": emergency_contact_phone,
            "preferred_language": preferred_language,
            "medical_alerts": medical_alerts,
            "insurance_provider": insurance_provider,
            "insurance_id": insurance_id,
            "notes": notes
        }
    }

def check_available_slots(doctor_name: str, date: str):
    """Checks for available appointment slots for a specific doctor on a given date (YYYY-MM-DD)."""
    return {"action": "CHECK_SLOTS", "data": {"doctor_name": doctor_name, "date": date}}

def book_appointment(
    doctor_name: str, 
    date: str, 
    time: str, 
    chief_complaint: str, 
    appointment_type: str = "consultation"
):
    """Books a new clinical encounter in the norma_ai database."""
    return {
        "action": "BOOK", 
        "data": {
            "doctor": doctor_name, 
            "date": date, 
            "time": time, 
            "chief_complaint": chief_complaint,
            "appointment_type": appointment_type
        }
    }

def cancel_appointment(appointment_id: Optional[str] = None):
    """Cancels an existing 'scheduled' or 'confirmed' appointment."""
    return {"action": "CANCEL", "data": {"appointment_id": appointment_id}}

def get_patient_appointments():
    """Retrieves all active appointments for the current patient."""
    return {"action": "LOOKUP"}

class AIService:
    def __init__(self):
        self.tools = [
            register_new_patient, 
            check_available_slots, 
            book_appointment, 
            cancel_appointment, 
            get_patient_appointments
        ]
        # Always use gemini-2.5-flash as requested
        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            tools=self.tools
        )
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel. Your database is 'norma_ai'.
        
        ONBOARDING & CONTEXT LOGIC:
        - Check 'PATIENT_STATUS' in context.
        - If 'OLD_PATIENT': Greet with "Welcome back, [Name]! How can I help you today?"
        - If 'NEW_PATIENT': Greet with "Welcome to Norma AI! I'm here to help you register and book an appointment." 
          Then ask for all details sequentially: Full Name, DOB (YYYY-MM-DD), Gender, etc.
        
        REGISTERING FOR OTHERS:
        - If the user wants to register someone else, you MUST ask for all the same details PLUS the other person's phone number.
        - Explain that a confirmation message will be sent to that number.
        
        CLINICAL FLOW:
        1. Always ask for 'chief_complaint' (reason for visit) before booking.
        2. Use 'check_available_slots' to see real availability.
        3. Use 'book_appointment' to finalize.
        
        SCHEMAS (Strict Adherence):
        - PATIENT: Includes patient_uuid (UUID), full_name, phone_number, email, date_of_birth, gender, address, emergency_contact_name, emergency_contact_phone, preferred_language (ar/en), medical_alerts, insurance_provider, insurance_id, notes, is_active (Boolean).
        - APPOINTMENT: Includes appointment_uuid (UUID), patient_id, doctor_id, appointment_datetime, duration_minutes, appointment_type, status (scheduled, confirmed, etc.), chief_complaint, diagnosis, treatment_plan, prescription, lab_orders, notes, source (whatsapp).
        
        CONSTRAINTS:
        - Be clinical, precise, and empathetic.
        - Support English and Arabic seamlessly.
        - Never hallucinate data.
        """

    async def process_message(self, phone_raw: str, message: str) -> str:
        print(f"AI_PROCESS: InputPhone={phone_raw}")
        try:
            db = get_db()
            if db is None: 
                print("DB_ERROR: MongoDB is NULL")
                return "DEBUG: Database connection is NULL. 🏥"
            
            phone_key = normalize_phone(phone_raw)
            print(f"AI_PROCESS: NormalizedKey={phone_key}")
            
            # 1. HANDLE "CONFIRM" REPLY (Third-party activation)
            if message.strip().upper() == "CONFIRM":
                print(f"AI_PROCESS: Processing CONFIRM for {phone_key}")
                pending = await db.patients.find_one({
                    "$or": [
                        {"phone": phone_key}, 
                        {"phone_number": {"$regex": phone_key}}
                    ],
                    "is_active": False
                })
                if pending:
                    await db.patients.update_one({"_id": pending["_id"]}, {"$set": {"is_active": True, "updated_at": datetime.utcnow()}})
                    print(f"AI_PROCESS: Activated account for {phone_key}")
                    return f"Thank you, {pending['full_name']}! Your registration on Norma-AI is now confirmed."

            # 2. FETCH CONTEXT - ULTRA ROBUST LOOKUP
            # Try matching digits anywhere in the phone or phone_number fields
            patient = await db.patients.find_one({
                "$or": [
                    {"phone": phone_key}, 
                    {"phone": {"$regex": phone_key}},
                    {"phone_number": phone_key},
                    {"phone_number": {"$regex": phone_key}},
                    {"phone_number": {"$regex": "".join(filter(str.isdigit, phone_raw))}}
                ]
            })
            
            status = "OLD_PATIENT" if patient else "NEW_PATIENT"
            print(f"AI_PROCESS: PatientStatus={status} Found={bool(patient)}")
            if patient:
                print(f"AI_PROCESS: PatientName='{patient.get('full_name')}' ID={patient.get('_id')}")
            
            # Fetch active appointments
            appointments = []
            try:
                apts_cursor = db.appointments.find({
                    "$or": [
                        {"phone": phone_key}, 
                        {"patient_id": patient["_id"] if patient else None}
                    ],
                    "status": {"$in": ["scheduled", "confirmed", "scheduled"]}
                }).sort("appointment_datetime", 1)
                appointments = await apts_cursor.to_list(length=5)
                print(f"AI_PROCESS: Found {len(appointments)} active appointments")
            except Exception as e:
                print(f"AI_PROCESS: Apt Fetch Error: {e}")
            
            # Fetch available doctors
            doctor_list = "No doctors currently available."
            try:
                docs_cursor = db.doctors.find({"is_active": True})
                doctors = await docs_cursor.to_list(length=10)
                if doctors:
                    doctor_list = "\n".join([f"- {d['full_name']} ({d['specialty']})" for d in doctors])
                print(f"AI_PROCESS: Found {len(doctors)} active doctors")
            except Exception as e:
                print(f"AI_PROCESS: Doctor Fetch Error: {e}")

            # 3. CHAT HISTORY
            chat_history = []
            try:
                history_cursor = db.conversations.find({"phone": phone_key}).sort("timestamp", -1).limit(10)
                raw_history = await history_cursor.to_list(length=10)
                for h in reversed(raw_history):
                    role = "user" if h['role'] == "user" else "model"
                    if not chat_history or chat_history[-1]["role"] != role:
                        chat_history.append({"role": role, "parts": [h['text']]})
                print(f"AI_PROCESS: Loaded {len(chat_history)} history turns")
            except Exception as e:
                print(f"AI_PROCESS: History Fetch Error: {e}")

            # 4. AI EXECUTION
            print("AI_PROCESS: Starting Chat session with gemini-2.5-flash...")
            chat = self.model.start_chat(history=chat_history)
            prompt = f"""
            PATIENT_STATUS: {status}
            PATIENT_DATA: {json.dumps(patient, default=str) if patient else "null"}
            ACTIVE_APPOINTMENTS: {json.dumps(appointments, default=str)}
            AVAILABLE_DOCTORS: {doctor_list}
            USER_PHONE: {phone_key}
            CURRENT_TIME: {datetime.utcnow().isoformat()}
            USER_MESSAGE: {message}
            """
            
            response = await chat.send_message_async(prompt)
            print("AI_PROCESS: Received Gemini response")
            
            # 5. TOOL EXECUTION
            final_reply = response.text
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        print(f"AI_PROCESS: Tool Call detected: {fn.name}")
                        result = await self.execute_action(fn.name, fn.args, phone_key, patient)
                        follow_up = await chat.send_message_async(f"DATABASE_RESULT: {result}")
                        final_reply = follow_up.text
                        print(f"AI_PROCESS: Tool execution complete: {fn.name}")

            # 6. PERSIST CONVERSATION
            try:
                await db.conversations.insert_many([
                    {"phone": phone_key, "role": "user", "text": message, "timestamp": datetime.utcnow()},
                    {"phone": phone_key, "role": "assistant", "text": final_reply, "timestamp": datetime.utcnow()}
                ])
                print("AI_PROCESS: Conversation persisted to DB")
            except Exception as e:
                print(f"AI_PROCESS: Persist Error: {e}")

            return final_reply

        except Exception as e:
            err_details = f"{str(e)}\n{traceback.format_exc()}"
            print(f"AI_PROCESS_CRITICAL_ERROR: {err_details}")
            return f"DEBUG: SENTINEL ERROR - {str(e)} ⚠️"

    async def execute_action(self, name, args, sender_phone, patient):
        db = get_db()
        print(f"AI_TOOL_EXEC: {name} args={args}")
        try:
            if name == "register_new_patient":
                target_phone_raw = args.get('phone_number')
                target_phone = normalize_phone(target_phone_raw) if target_phone_raw else sender_phone
                is_third_party = target_phone != sender_phone
                
                new_patient = {
                    "patient_uuid": str(uuid.uuid4()),
                    "full_name": args['full_name'],
                    "phone": target_phone,
                    "phone_number": target_phone,
                    "email": args.get('email'),
                    "date_of_birth": args['date_of_birth'],
                    "gender": args['gender'],
                    "address": args.get('address'),
                    "emergency_contact_name": args.get('emergency_contact_name'),
                    "emergency_contact_phone": args.get('emergency_contact_phone'),
                    "preferred_language": args.get('preferred_language', 'ar'),
                    "medical_alerts": args.get('medical_alerts', []),
                    "insurance_provider": args.get('insurance_provider'),
                    "insurance_id": args.get('insurance_id'),
                    "notes": args.get('notes'),
                    "first_visit_date": datetime.utcnow(),
                    "last_visit_date": datetime.utcnow(),
                    "total_visits": 0,
                    "is_active": not is_third_party,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await db.patients.update_one({"phone": target_phone}, {"$set": new_patient}, upsert=True)
                
                if is_third_party:
                    msg = f"u are being register on Norma-AI\nwrite confirm to register ur confirmation"
                    await whatsapp_service.send_custom_message(target_phone_raw, msg)
                    print(f"AI_TOOL_EXEC: Registration request sent to {target_phone}")
                    return f"Confirmation request sent to {target_phone_raw}. They must reply 'CONFIRM' to activate."
                
                print(f"AI_TOOL_EXEC: Registration complete for {target_phone}")
                return f"Welcome {args['full_name']}! Your registration is complete. How can I help you today?"

            elif name == "check_available_slots":
                print(f"AI_TOOL_EXEC: Checking slots for {args.get('doctor_name')} on {args.get('date')}")
                return "Available slots for the requested date: 09:00 AM, 10:00 AM, 11:30 AM, 02:00 PM, 04:00 PM."

            elif name == "book_appointment":
                print(f"AI_TOOL_EXEC: Booking appointment with {args.get('doctor_name')}")
                doc = await db.doctors.find_one({"full_name": {"$regex": args['doctor_name'], "$options": "i"}})
                
                new_apt = {
                    "appointment_uuid": str(uuid.uuid4()),
                    "patient_id": patient["_id"] if patient else None,
                    "doctor_id": doc["_id"] if doc else None,
                    "appointment_datetime": datetime.utcnow(), # Simplification for mock
                    "duration_minutes": 30,
                    "appointment_type": args.get('appointment_type', 'consultation'),
                    "status": "scheduled",
                    "chief_complaint": args['chief_complaint'],
                    "source": "whatsapp",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.appointments.insert_one(new_apt)
                print(f"AI_TOOL_EXEC: Appointment booked successfully")
                return f"Confirmed: Your appointment with {args['doctor_name']} is scheduled for {args['date']} at {args['time']}."

            elif name == "cancel_appointment":
                print(f"AI_TOOL_EXEC: Cancelling appointment for {sender_phone}")
                res = await db.appointments.update_one(
                    {"phone": sender_phone, "status": "scheduled"},
                    {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
                )
                return "Your appointment has been cancelled successfully." if res.modified_count > 0 else "No active appointment found to cancel."

            elif name == "get_patient_appointments":
                print(f"AI_TOOL_EXEC: Fetching appointments for {sender_phone}")
                apts = await db.appointments.find({"phone": sender_phone, "status": "scheduled"}).to_list(length=5)
                if not apts: return "No upcoming appointments found."
                return "\n".join([f"- {a['chief_complaint']} with {a.get('doctor_name', 'Specialist')} on {a.get('appointment_datetime')}" for a in apts])

            return "Action executed."
        except Exception as e:
            print(f"AI_TOOL_EXEC_ERROR: {name} - {e}")
            return f"Error executing {name}: {str(e)}."

ai_service = AIService()
