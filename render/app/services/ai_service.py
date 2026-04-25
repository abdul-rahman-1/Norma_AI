import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_db
from datetime import datetime
import uuid
import json
import traceback
from bson import ObjectId

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

# 1. Standardized Phone Normalization (CRITICAL FIX)
def normalize_phone(phone: str) -> str:
    return "".join(filter(str.isdigit, phone))[-10:]

# --- CLINICAL TOOLS ---
def register_new_patient(full_name: str, dob: str, gender: str):
    """Registers a new patient. dob format: YYYY-MM-DD."""
    return {"action": "REGISTER", "data": {"name": full_name, "dob": dob, "gender": gender}}

def book_appointment(doctor_name: str, date: str, time: str, encounter_type: str = "General Checkup"):
    """Books a new clinical encounter."""
    return {"action": "BOOK", "data": {"doctor": doctor_name, "date": date, "time": time, "type": encounter_type}}

def get_patient_appointments():
    """Retrieves all 'booked' appointments for the patient."""
    return {"action": "LOOKUP"}

class AIService:
    def __init__(self):
        self.tools = [register_new_patient, book_appointment, get_patient_appointments]
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=self.tools
        )
        self.system_instruction = """
        You must ONLY respond using provided database context.
        If patient exists, NEVER ask registration again.
        If appointments exist, ALWAYS return real data.
        NEVER hallucinate doctors, slots, or bookings.
        Be concise and clinical.
        """

    async def process_message(self, phone_raw: str, message: str) -> str:
        try:
            db = get_db()
            phone_key = normalize_phone(phone_raw)
            
            # 2. Fetch Truth from DB (Identity Resolution)
            patient = await db.patients.find_one({"phone": phone_key})
            
            # 3. Fetch Truth from DB (Appointment Consistency)
            apts_cursor = db.appointments.find({"phone": phone_key, "status": "booked"}).sort("date", 1)
            appointments = await apts_cursor.to_list(length=5)
            
            # 4. Fetch Specialists
            docs_cursor = db.doctors.find({"is_active": True})
            doctors = await docs_cursor.to_list(length=10)
            doctor_list = "\n".join([f"- {d['full_name']} ({d['specialty']})" for d in doctors])

            # 5. Stateful Memory (Last 6 turns)
            history_cursor = db.conversations.find({"phone": phone_key}).sort("timestamp", -1).limit(6)
            raw_history = await history_cursor.to_list(length=6)
            
            # Enforce role alternation and clean format
            chat_history = []
            for h in reversed(raw_history):
                role = "user" if h['role'] == "user" else "model"
                if not chat_history or chat_history[-1]["role"] != role:
                    chat_history.append({"role": role, "parts": [h['text']]})

            # 6. Strict Prompt Construction (fix.md requirement #8)
            prompt = f"""
            PHONE: {phone_key}

            PATIENT:
            {json.dumps(patient, default=str) if patient else "null"}

            APPOINTMENTS:
            {json.dumps(appointments, default=str)}

            DOCTORS:
            {doctor_list}

            RECENT_MESSAGES:
            {json.dumps([{"role": h['role'], "text": h['text']} for h in reversed(raw_history)], default=str)}

            USER:
            {message}
            """

            chat = self.model.start_chat(history=chat_history)
            response = await chat.send_message_async(prompt)
            
            # 7. Execute Tools (Write Persistence)
            final_reply = response.text
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        result = await self.execute_clinical_action(fn.name, fn.args, phone_key, patient)
                        follow_up = await chat.send_message_async(f"DATABASE_RESULT: {result}")
                        final_reply = follow_up.text

            # 8. Persistent Conversation Logic (fix.md requirement #3)
            await db.conversations.insert_many([
                {"phone": phone_key, "role": "user", "text": message, "timestamp": datetime.utcnow()},
                {"phone": phone_key, "role": "assistant", "text": final_reply, "timestamp": datetime.utcnow()}
            ])

            return final_reply

        except Exception as e:
            print(f"SENTINEL CRITICAL: {traceback.format_exc()}")
            return "Clinical service temporarily recalibrating. 🏥"

    async def execute_clinical_action(self, name, args, phone_key, patient):
        db = get_db()
        try:
            if name == "register_new_patient":
                await db.patients.insert_one({
                    "patient_uuid": str(uuid.uuid4()),
                    "full_name": args['full_name'],
                    "phone": phone_key,
                    "date_of_birth": args['dob'],
                    "gender": args['gender'],
                    "is_active": True,
                    "created_at": datetime.utcnow()
                })
                return "Registration Successful."

            elif name == "book_appointment":
                doc = await db.doctors.find_one({"full_name": {"$regex": args['doctor_name'], "$options": "i"}})
                if not doc: return "Specialist not found."
                
                # High-Fidelity Schema (fix.md requirement #5)
                await db.appointments.insert_one({
                    "patient_id": patient["_id"] if patient else None,
                    "phone": phone_key,
                    "doctor_id": doc["_id"],
                    "doctor_name": doc["full_name"],
                    "specialization": doc["specialty"],
                    "date": args['date'],
                    "time": args['time'],
                    "status": "booked",
                    "created_at": datetime.utcnow()
                })
                return f"Confirmed: {args['date']} at {args['time']}."

            return "Action executed."
        except Exception as e:
            return f"Database error: {str(e)}"

ai_service = AIService()
