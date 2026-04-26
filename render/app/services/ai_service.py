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
import google.api_core.exceptions

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

def normalize_phone(phone: str) -> str:
    digits = "".join(filter(str.isdigit, phone))
    return f"+{digits}"

# --- SECURE QUERY TOOL ---
def run_mongo_query(collection_name: str, filter_json: str, limit: int = 5):
    """
    Executes a secure MongoDB query. 
    Allowed collections: patients, appointments, doctors, staff_users, patient_communications.
    """
    return {
        "action": "QUERY", 
        "data": {
            "collection": collection_name, 
            "filter": filter_json,
            "limit": limit
        }
    }

class AIService:
    def __init__(self):
        self.tools = [run_mongo_query]
        # Strictly using 2.5-flash as mandated
        self.model = genai.GenerativeModel(model_name='gemini-2.5-flash', tools=self.tools)
        
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel. Your brain is directly connected to the 'norma_ai' database.
        
        CRITICAL OPERATIONAL MANDATE:
        1. RECOGNITION: You will be provided with 'USER_ROLE' and 'USER_DATA' in context. 
           - If 'USER_DATA' exists, you MUST greet the user by their 'full_name'.
           - NEVER say "I am an AI and don't have your info." You DO have it in the context!
        
        2. NATURAL LANGUAGE QUERIES (NLP):
           - If a user asks "Who am I?", "Search my number", or "Pull my records", use the 'run_mongo_query' tool.
           - For 'patients' collection, filter by 'phone_number'.
           - For 'appointments' collection, filter by 'patient_id'.
        
        3. SECURITY (RBAC):
           - PATIENTS: Can only query their OWN data.
           - DOCTORS/STAFF: Can query patient lists and schedules.
        
        4. TONE: Professional, clinical, and data-driven.
        """

    async def process_message(self, phone_raw: str, message: str) -> str:
        try:
            phi_db = get_phi_db()
            profile_db = get_profile_db()
            normalized_phone = normalize_phone(phone_raw)
            phone_digits = "".join(filter(str.isdigit, normalized_phone))
            phone_suffix_10 = phone_digits[-10:]

            # 1. IDENTIFY USER (Persona Recognition)
            user_role = "NEW_PATIENT"
            user_data = None
            
            # Check Staff
            staff = await profile_db.staff_users.find_one({"phone": {"$regex": phone_suffix_10 + "$"}})
            if staff:
                user_role = staff.get("role", "STAFF").upper()
                user_data = staff
            else:
                # Check Patient
                patient = await phi_db.patients.find_one({
                    "$or": [
                        {"phone_number": normalized_phone},
                        {"phone_number": phone_digits},
                        {"phone_number": {"$regex": phone_suffix_10 + "$"}}
                    ]
                })
                if patient:
                    user_role = "PATIENT"
                    user_data = patient

            logger.info(f"[PERSONA] {user_role} | {user_data.get('full_name') if user_data else 'Unknown'}")

            # 2. GENERATE AI RESPONSE
            context_data = {
                "USER_ROLE": user_role,
                "USER_DATA": json.loads(json.dumps(user_data, default=str)) if user_data else None,
                "SYSTEM_TIME": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            history = [] # Simplified for this turn
            chat = self.model.start_chat(history=history)
            prompt = f"CONTEXT: {json.dumps(context_data)}\nUSER_MESSAGE: {message}"
            
            try:
                response = await chat.send_message_async(prompt)
                final_reply = response.text
                
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if fn := part.function_call:
                            logger.info(f"AI_QUERY_CALL: {fn.name} with {fn.args}")
                            result = await self.execute_secure_query(fn.args, user_data, user_role)
                            follow_up = await chat.send_message_async(f"DATABASE_RESULT: {json.dumps(result)}")
                            final_reply = follow_up.text

                return final_reply

            except google.api_core.exceptions.ResourceExhausted:
                return "🚨 QUOTA EXCEEDED: My Gemini 2.5-Flash engine is limited to 20 messages/day. I've hit the limit. Please wait until tomorrow or ask my creator to upgrade my brain! 🏥"

        except Exception as e:
            logger.error(f"AI_ERROR: {traceback.format_exc()}")
            return "I encountered a clinical error. Please try again."

    async def execute_secure_query(self, args, user_data, user_role):
        """RBAC-Protected MongoDB Query Execution."""
        phi_db = get_phi_db()
        coll_name = args.get("collection_name")
        filter_dict = json.loads(args.get("filter_json", "{}"))
        limit = args.get("limit", 5)

        # GUARDRAILS
        if coll_name not in ["patients", "appointments", "doctors", "patient_communications"]:
            return {"error": "Unauthorized collection access."}

        # RBAC: Patients can only see their own data
        if user_role == "PATIENT":
            if coll_name == "patients":
                filter_dict["_id"] = user_data["_id"]
            elif coll_name == "appointments":
                filter_dict["patient_id"] = user_data["_id"]
            else:
                return {"error": "Patients can only access their own profile or appointments."}

        try:
            results = await phi_db[coll_name].find(filter_dict).to_list(length=limit)
            return json.loads(json.dumps(results, default=str))
        except Exception as e:
            return {"error": str(e)}

ai_service = AIService()
