You are a senior backend engineer.

Refactor the NORMA AI backend (Python, FastAPI, MongoDB, Gemini, Twilio WhatsApp) to FIX state persistence, identity resolution, and appointment consistency.

DO NOT rewrite everything. MODIFY existing files inside /backend and /render.

-------------------------------------
CRITICAL PROBLEMS TO FIX
-------------------------------------

1. Phone number inconsistency:
- Currently mixing formats:
  "whatsapp:+91..."
  "+91..."
  last 10 digits
- This breaks DB lookups.

FIX:
- Create function:

def normalize_phone(phone: str) -> str:
    return "".join(filter(str.isdigit, phone))[-10:]

- Use this EVERYWHERE:
  patients
  appointments
  conversations

-------------------------------------

2. Patient lookup is incorrect:
- Current code uses regex on phone_number
- Replace with exact match:

patient = db.patients.find_one({ "phone": phone_key })

- Store phone as:
  "phone": "9876543210"

-------------------------------------

3. Conversations are NOT stored:
- System reads history but never writes it.

FIX:
- After every message:
  store BOTH user + assistant messages

Structure:
{
  "phone": phone_key,
  "role": "user" | "assistant",
  "text": "...",
  "timestamp": ISODate
}

- Only keep last 6 messages per user:
  implement trimming or query limit

-------------------------------------

4. Appointments are not used as source of truth:
- Gemini is hallucinating because DB data is not injected.

FIX:
- BEFORE calling Gemini:
  fetch:

appointments = db.appointments.find({
  "phone": phone_key,
  "status": "booked"
})

- Pass into prompt as structured JSON

-------------------------------------

5. Appointment schema is incomplete:

UPDATE appointment insert:

{
  "patient_id": ObjectId,
  "phone": phone_key,
  "doctor_id": ObjectId,
  "doctor_name": string,
  "specialization": string,
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "status": "booked",
  "created_at": ISODate
}

-------------------------------------

6. Tool execution logic is weak:

FIX tools:

register_new_patient →
  must insert into DB

book_appointment →
  must insert appointment

get_patient_appointments →
  must return DB data ALWAYS

-------------------------------------

7. Gemini must NOT decide facts:

UPDATE system instruction:

"You must ONLY respond using provided database context.
If patient exists, NEVER ask registration again.
If appointments exist, ALWAYS return real data.
NEVER hallucinate doctors, slots, or bookings."

-------------------------------------

8. Prompt construction is insufficient:

REPLACE prompt with:

prompt = f'''
PHONE: {phone_key}

PATIENT:
{patient_json_or_null}

APPOINTMENTS:
{appointments_json}

DOCTORS:
{doctor_list}

RECENT_MESSAGES:
{last_6_messages}

USER:
{message}
'''

-------------------------------------

9. Chat history must be controlled:

- Use last 6 messages only
- Enforce role alternation
- Do NOT rely on Gemini memory

-------------------------------------

10. Bug after restart (main issue):

Ensure:
- Patient lookup works via phone_key
- Appointment lookup works via phone_key
- Conversation is stored and retrieved

-------------------------------------

OUTPUT REQUIREMENTS
-------------------------------------

Return:

1. Updated AI service file (clean, production ready)
2. Updated Mongo queries
3. Fixed tool execution
4. Proper conversation storage logic
5. No breaking of existing folder structure
6. Add comments explaining each fix

-------------------------------------

DO NOT:
- Change framework
- Remove Gemini tools
- Rewrite entire project
- Introduce unnecessary abstractions

-------------------------------------

GOAL
-------------------------------------

After fix:

User books appointment →
Restart server →
User asks "do I have appointment?" →
System correctly returns booked appointment from DB

-------------------------------------