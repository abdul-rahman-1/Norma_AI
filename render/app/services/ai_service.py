import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_db
from datetime import datetime, timedelta
import uuid
import traceback
from bson import ObjectId

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

# --- CLINICAL TOOLS DEFINITION ---

def register_new_patient(full_name: str, dob_yyyy_mm_dd: str, gender: str):
    """
    Registers a new patient into the clinical mesh.
    Use this ONLY if the system explicitly identifies the user as 'New' or 'Unknown'.
    """
    return {"action": "register", "data": {"name": full_name, "dob": dob_yyyy_mm_dd, "gender": gender}}

def book_appointment(doctor_name: str, date_yyyy_mm_dd: str, time_hh_mm: str, encounter_type: str = "General Checkup"):
    """
    Schedules a new clinical encounter.
    Requires doctor name, date, and time.
    """
    return {"action": "book", "data": {"doctor": doctor_name, "date": date_yyyy_mm_dd, "time": time_hh_mm, "type": encounter_type}}

def get_patient_appointments():
    """
    Retrieves the current scheduled appointments for the patient from the database.
    Always call this before stating the patient has no appointments.
    """
    return {"action": "lookup"}

def cancel_appointment(appointment_id: str):
    """
    Cancels a specific clinical encounter using its unique ID.
    """
    return {"action": "cancel", "data": {"id": appointment_id}}

class AIService:
    def __init__(self):
        # Initialize tools
        self.tools = [register_new_patient, book_appointment, get_patient_appointments, cancel_appointment]
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=self.tools
        )
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel, a stateful medical orchestration agent.
        
        CORE OPERATING PROTOCOLS:
        1. IDENTITY: You are provided with 'KNOWN_PATIENT' data. If it exists, greet them by name and show their Age.
        2. DATABASE FIRST: Never assume clinical facts. Always use 'get_patient_appointments' if asked about the schedule.
        3. REGISTRATION: New patients MUST provide Full Name, DOB (YYYY-MM-DD), and Gender before any booking.
        4. BREVITY: Responses must be professional, clinical, and formatted for WhatsApp (use emojis sparingly).
        5. CURRENT DATE: 2026-04-25.
        """

    async def process_message(self, phone: str, message: str) -> str:
        try:
            db = get_db()
            if db is None: return "Clinical mesh offline. Please contact support. 🏥"

            # 1. Hardened Identity Search (Match last 10 digits)
            clean_phone = "".join(filter(str.isdigit, phone))[-10:]
            patient = await db.patients.find_one({"phone_number": {"$regex": clean_phone}})
            
            patient_context = "None (Unknown Patient)"
            if patient:
                age = "N/A"
                if patient.get('date_of_birth'):
                    dob = patient['date_of_birth']
                    if hasattr(dob, 'year'):
                        age = datetime.utcnow().year - dob.year
                patient_context = {
                    "name": patient['full_name'],
                    "id": str(patient['_id']),
                    "age": age,
                    "phone": patient['phone_number']
                }

            # 2. Fetch Specialists
            doctors = await db.doctors.find({"is_active": True}).to_list(length=10)
            doc_info = "\n".join([f"- {d['full_name']} ({d['specialty']})" for d in doctors])

            # 3. Conversational Memory (Last 6 messages)
            history_cursor = db.conversations.find({"phone": phone}).sort("timestamp", -1).limit(6)
            raw_history = await history_cursor.to_list(length=6)
            chat_history = [{"role": "user" if h['role']=="user" else "model", "parts": [h['text']]} for h in reversed(raw_history)]

            # 4. Start Chat Session with Memory
            chat = self.model.start_chat(history=chat_history)
            
            prompt = f"""
            {self.system_instruction}
            
            CLINICAL CONTEXT:
            - SENDER_PHONE: {phone}
            - KNOWN_PATIENT: {patient_context}
            - AVAILABLE_SPECIALISTS: {doc_info}
            - CURRENT_UTC_TIME: {datetime.utcnow().isoformat()}

            USER_INPUT: "{message}"
            """
            
            response = await chat.send_message_async(prompt)
            
            # 5. Handle Function Calls
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if fn := part.function_call:
                        print(f"SENTINEL EXECUTE: {fn.name}")
                        tool_result = await self.execute_clinical_action(fn.name, fn.args, phone, patient)
                        
                        # Feed the database result back to AI for a finalized human response
                        follow_up = await chat.send_message_async(f"DATABASE_RESULT for {fn.name}: {tool_result}")
                        response = follow_up

            final_text = response.text

            # 6. Save History
            await db.conversations.insert_one({"phone": phone, "role": "user", "text": message, "timestamp": datetime.utcnow()})
            await db.conversations.insert_one({"phone": phone, "role": "ai", "text": final_text, "timestamp": datetime.utcnow()})

            return final_text

        except Exception as e:
            print(f"SENTINEL CRITICAL: {traceback.format_exc()}")
            return "Sentinel under clinical recalibration. Please retry your request. ⚠️"

    async def execute_clinical_action(self, name: str, args: dict, phone: str, patient: dict):
        db = get_db()
        try:
            if name == "register_new_patient":
                new_patient = {
                    "patient_uuid": str(uuid.uuid4()),
                    "full_name": args['full_name'],
                    "phone_number": phone,
                    "date_of_birth": datetime.fromisoformat(args['dob_yyyy_mm_dd']),
                    "gender": args['gender'],
                    "is_active": True,
                    "created_at": datetime.utcnow()
                }
                await db.patients.insert_one(new_patient)
                return "Registration Successful."

            elif name == "get_patient_appointments":
                if not patient: return "No patient record found."
                apts_cursor = db.appointments.find({"patient_id": patient["_id"]}).sort("scheduled_at", 1)
                apts = await apts_cursor.to_list(length=10)
                if not apts: return "No appointments found."
                
                res = []
                for a in apts:
                    doc = await db.doctors.find_one({"_id": a["doctor_id"]})
                    res.append(f"ID: {str(a['_id'])} | {a['type']} with {doc['full_name']} at {a['scheduled_at'].strftime('%Y-%m-%d %H:%M')}")
                return "\n".join(res)

            elif name == "book_appointment":
                if not patient: return "Registration required before booking."
                doctor = await db.doctors.find_one({"full_name": {"$regex": args['doctor_name'], "$options": "i"}})
                if not doctor: return "Specialist not found."
                
                new_apt = {
                    "patient_id": patient["_id"],
                    "doctor_id": doctor["_id"],
                    "scheduled_at": datetime.fromisoformat(f"{args['date_yyyy_mm_dd']}T{args['time_hh_mm']}"),
                    "status": "booked",
                    "type": args.get('encounter_type', 'General Checkup'),
                    "source": "whatsapp_orchestrator",
                    "created_at": datetime.utcnow()
                }
                await db.appointments.insert_one(new_apt)
                return f"Booking confirmed with {doctor['full_name']}."

            elif name == "cancel_appointment":
                res = await db.appointments.update_one({"_id": ObjectId(args['appointment_id'])}, {"$set": {"status": "canceled"}})
                return "Appointment canceled." if res.modified_count > 0 else "Appointment not found."

        except Exception as e:
            return f"Error executing clinical tool: {str(e)}"

ai_service = AIService()
