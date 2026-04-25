import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_db
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

def print(msg):
    print(msg)
    sys.stdout.flush()

def normalize_phone(phone: str) -> str:
    """Standardizes phone numbers to E.164 format or at least a consistent numeric string."""
    digits = "".join(filter(str.isdigit, phone))
    if not phone.startswith('+') and len(digits) == 10:
        # We still need a way to handle local numbers if the country code is missing, 
        # but let's make it less regional-specific or at least better documented.
        # For now, let's just ensure it's a full string of digits.
        pass
    return f"+{digits}" if not phone.startswith('+') else phone

# --- CLINICAL TOOLS ---
def register_new_patient(
    full_name: str, date_of_birth: str, gender: str, phone_number: Optional[str] = None,
    email: Optional[str] = None, address: Optional[str] = None, notes: Optional[str] = None,
    preferred_language: str = "en", insurance_provider: Optional[str] = None,
    insurance_id: Optional[str] = None
):
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
    return {"action": "CHECK_SLOTS", "data": {"doctor_name": doctor_name, "date": date}}

def book_appointment(doctor_name: str, date: str, time: str, chief_complaint: str):
    return {
        "action": "BOOK", 
        "data": {
            "doctor_name": doctor_name, "date": date, "time": time, 
            "chief_complaint": chief_complaint
        }
    }

def cancel_appointment(appointment_id: str):
    return {"action": "CANCEL", "data": {"appointment_id": appointment_id}}

def get_patient_appointments():
    return {"action": "LOOKUP"}

class AIService:
    def __init__(self):
        self.tools = [register_new_patient, check_available_slots, book_appointment, cancel_appointment, get_patient_appointments]
        # Strictly using gemini-2.5-flash per user instruction
        self.model = genai.GenerativeModel(model_name='gemini-2.5-flash', tools=self.tools)
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel. Your database is 'norma_ai'.
        
        ONBOARDING & CONTEXT LOGIC:
        - Check 'PATIENT_STATUS' in context.
        - If 'OLD_PATIENT': Greet with "Welcome back, [Name]! How can I help you today?"
        - If 'NEW_PATIENT': Greet with "Welcome to Norma AI! I'm here to help you register and book an appointment." 
          Then ask for all details sequentially: Full Name, DOB (YYYY-MM-DD), Gender.
        
        TOOLS USAGE:
        - Use 'check_available_slots' to see when a doctor is free.
        - Use 'book_appointment' ONLY after confirming the doctor, date, and time with the patient.
        - Use 'register_new_patient' for new users.
        - Use 'get_patient_appointments' to show their upcoming visits.
        """

    async def process_message(self, phone_raw: str, message: str) -> str:
        try:
            db = get_db()
            if db is None: 
                return "I'm sorry, I'm having trouble connecting to my clinical database right now. Please try again in a few moments. 🏥"
            
            normalized_phone = normalize_phone(phone_raw)
            # Extract last 10 digits for robust matching
            phone_digits = "".join(filter(str.isdigit, normalized_phone))
            phone_suffix_10 = phone_digits[-10:] if len(phone_digits) >= 10 else phone_digits
            
            print(f"AI_PROCESS: RawPhone={phone_raw} Normalized={normalized_phone} Suffix={phone_suffix_10}")
            
            # 1. FETCH PATIENT - Recognition fix using suffix-based regex
            # This handles numbers stored with spaces, country codes, or different formats
            patient = await db.patients.find_one({
                "$or": [
                    {"phone_number": normalized_phone},
                    {"phone_number": {"$regex": phone_suffix_10 + "$"}}
                ]
            })
            
            status = "OLD_PATIENT" if patient else "NEW_PATIENT"
            print(f"AI_STATUS: {status} (Found={bool(patient)})")
            
            # 2. FETCH CONTEXT DATA
            appointments = []
            if patient:
                apts_cursor = db.appointments.find({"patient_id": patient["_id"]}).sort("scheduled_at", 1)
                appointments = await apts_cursor.to_list(length=5)
            
            docs = await db.doctors.find({"status": "active"}).to_list(length=10)
            doctor_list = "\n".join([f"- {d['full_name']} ({d.get('specialization', d.get('specialty', 'General'))})" for d in docs])

            # 3. CONVERSATION HISTORY
            chat_history = []
            history = await db.conversations.find({"phone": normalized_phone}).sort("timestamp", -1).limit(15).to_list(length=15)
            for h in reversed(history):
                role = "user" if h['role'] == "user" else "model"
                if chat_history and chat_history[-1]["role"] == role:
                    chat_history[-1]["parts"].append(h['text'])
                else:
                    chat_history.append({"role": role, "parts": [h['text']]})

            # 4. AI EXECUTION
            chat = self.model.start_chat(history=chat_history)
            context_prompt = (
                f"PATIENT_STATUS: {status}\n"
                f"PATIENT_DATA: {json.dumps(patient, default=str)}\n"
                f"ACTIVE_APPOINTMENTS: {json.dumps(appointments, default=str)}\n"
                f"AVAILABLE_DOCTORS: {doctor_list}\n"
                f"USER_PHONE: {normalized_phone}\n"
                f"USER_MESSAGE: {message}"
            )
            
            response = await chat.send_message_async(context_prompt)
            final_reply = response.text
            
            # Handle tool calls
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        result = await self.execute_action(fn.name, fn.args, normalized_phone, patient)
                        follow_up = await chat.send_message_async(f"DATABASE_RESULT: {json.dumps(result)}")
                        final_reply = follow_up.text

            # Save to history
            await db.conversations.insert_many([
                {"phone": normalized_phone, "role": "user", "text": message, "timestamp": datetime.utcnow()},
                {"phone": normalized_phone, "role": "assistant", "text": final_reply, "timestamp": datetime.utcnow()}
            ])

            return final_reply

        except Exception as e:
            print(f"AI_CRITICAL_ERROR: {traceback.format_exc()}")
            return "I encountered an error while processing your request. Please try again."

    async def execute_action(self, name, args, sender_phone, patient):
        db = get_db()
        print(f"TOOL_EXEC: {name} with args {args}")
        try:
            if name == "register_new_patient":
                # Handle Date conversion
                dob_val = args['date_of_birth']
                try:
                    dob_dt = datetime.strptime(dob_val, "%Y-%m-%d")
                except:
                    try: dob_dt = datetime.strptime(dob_val, "%d-%m-%Y")
                    except: dob_dt = dob_val # Fallback to string if parsing fails
                
                new_patient = {
                    "patient_uuid": str(uuid.uuid4()),
                    "full_name": args['full_name'],
                    "phone_number": sender_phone,
                    "date_of_birth": dob_dt,
                    "gender": args['gender'],
                    "email": args.get('email', ""),
                    "address": args.get('address', ""),
                    "notes": args.get('notes', ""),
                    "preferred_language": args.get('preferred_language', "en"),
                    "insurance_provider": args.get('insurance_provider', ""),
                    "insurance_id": args.get('insurance_id', ""),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.patients.update_one(
                    {"phone_number": sender_phone}, 
                    {"$set": new_patient}, 
                    upsert=True
                )
                return {"status": "success", "message": f"Patient {args['full_name']} registered."}
            
            elif name == "book_appointment":
                if not patient:
                    return {"status": "error", "message": "Patient must be registered before booking."}
                
                doctor = await db.doctors.find_one({"full_name": {"$regex": args['doctor_name'], "$options": "i"}})
                if not doctor:
                    return {"status": "error", "message": f"Doctor {args['doctor_name']} not found."}

                new_apt = {
                    "patient_id": patient["_id"],
                    "doctor_id": doctor["_id"],
                    "scheduled_at": f"{args['date']} {args['time']}",
                    "status": "booked",
                    "reason": args['chief_complaint'],
                    "source": "whatsapp",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.appointments.insert_one(new_apt)
                return {"status": "success", "message": "Appointment booked successfully."}

            elif name == "check_available_slots":
                doctor = await db.doctors.find_one({"full_name": {"$regex": args['doctor_name'], "$options": "i"}})
                if not doctor:
                    return {"status": "error", "message": "Doctor not found."}
                return {"status": "success", "slots": ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM"]}

            elif name == "cancel_appointment":
                res = await db.appointments.update_one(
                    {"_id": ObjectId(args['appointment_id']) if 'appointment_id' in args else None},
                    {"$set": {"status": "canceled", "updated_at": datetime.utcnow()}}
                )
                return {"status": "success", "message": "Appointment canceled."}

            elif name == "get_patient_appointments":
                if not patient: return {"status": "error", "message": "Patient not found."}
                apts = await db.appointments.find({"patient_id": patient["_id"]}).to_list(length=10)
                return {"status": "success", "appointments": json.loads(json.dumps(apts, default=str))}
            
            return {"status": "error", "message": "Unknown tool."}
        except Exception as e:
            print(f"TOOL_ERROR: {e}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            print(f"TOOL_ERROR: {e}")
            return f"Error executing {name}."

ai_service = AIService()
