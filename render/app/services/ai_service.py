import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_phi_db, get_profile_db
from app.logger import logger
from datetime import datetime
import json
import traceback
import uuid

# Import Modular Features
from app.features.patient_ops import execute_patient_op
from app.features.staff_ops import execute_staff_op
from app.features.registration_ops import execute_registration
from app.features.medical_ops import execute_medical_op
from app.features.billing_ops import execute_billing_op

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

def normalize_phone(phone: str) -> str:
    digits = "".join(filter(str.isdigit, phone))
    return f"+{digits}"

def run_clinical_operation(operation_type: str, params: str):
    """MASTER TOOL: Routes logic across all 18 clinical collections."""
    return {"action": "EXECUTE", "data": {"type": operation_type, "params": params}}

class AIService:
    def __init__(self):
        self.tools = [run_clinical_operation]
        self.system_instruction = """
        You are the NORMA AI Clinical Sentinel. 
        
        ROLE DISCOVERY FLOW:
        - If a user asks "What can you help me with?" or generic features:
          1. ASK the user if they are a Patient, a Doctor, or a Staff member.
          2. ONLY THEN explain the features for that specific role.
        
        REGISTRATION GUARDRAILS:
        - PATIENTS can register themselves.
        - STAFF can register Patients.
        - DOCTORS can register Staff (PAs).
        - ADMINS can register Doctors.
        - If a user tries to register someone above their rank, politely decline.
        
        AUTONOMY: Use 'run_clinical_operation' to execute any logic across the system.
        """
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash', 
            tools=self.tools,
            system_instruction=self.system_instruction
        )

    async def process_message(self, phone_raw: str, message: str) -> str:
        try:
            phi_db = get_phi_db()
            profile_db = get_profile_db()
            normalized_phone = normalize_phone(phone_raw)
            phone_digits = "".join(filter(str.isdigit, normalized_phone))
            phone_suffix_10 = phone_digits[-10:]

            # 1. PERSONA IDENTIFICATION
            user_role = "NEW_PATIENT"
            user_data = None
            
            # Check Staff/Doctors/Admins
            staff = await profile_db.staff_users.find_one({"phone": {"$regex": phone_suffix_10 + "$"}})
            if staff:
                # Includes ADMIN if role is set to "ADMIN"
                user_role = staff.get("role", "STAFF").upper()
                user_data = staff
            else:
                doc = await profile_db.doctors.find_one({"whatsapp_number": {"$regex": phone_suffix_10 + "$"}})
                if doc:
                    user_role = "DOCTOR"
                    user_data = doc
                else:
                    patient = await phi_db.patients.find_one({"phone_number": {"$regex": phone_suffix_10 + "$"}})
                    if patient:
                        user_role = "PATIENT"
                        user_data = patient

            # 2. CONVERSATION HISTORY (Memory)
            convo = await phi_db.conversations.find_one({"phone": normalized_phone})
            db_history = convo.get("messages", []) if convo else []
            
            formatted_history = []
            for msg in db_history:
                # We skip tool calls in saved history for simplicity and reliability
                formatted_history.append({"role": msg["role"], "parts": [msg["text"]]})

            # 3. AI EXECUTION
            context = {"USER_ROLE": user_role, "USER_DATA": json.loads(json.dumps(user_data, default=str)) if user_data else None}
            chat = self.model.start_chat(history=formatted_history)
            prompt = f"CONTEXT: {json.dumps(context)}\nMESSAGE: {message}"
            
            response = await chat.send_message_async(prompt)
            
            # Recursive Tool Call Loop
            for _ in range(3):
                if not response.candidates or not response.candidates[0].content.parts:
                    break
                
                parts = response.candidates[0].content.parts
                tool_calls = [p.function_call for p in parts if p.function_call]
                
                if not tool_calls:
                    break
                
                logger.info(f"AI requested {len(tool_calls)} tool calls.")
                tool_responses = []
                for fn in tool_calls:
                    try:
                        # args in function_call is a map, we extract them
                        args = {k: v for k, v in fn.args.items()}
                        result = await self.route_operation(args, user_data, user_role, normalized_phone)
                        tool_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fn.name,
                                    response={"result": result}
                                )
                            )
                        )
                    except Exception as e:
                        logger.error(f"TOOL_CALL_ERROR: {traceback.format_exc()}")
                        tool_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=fn.name,
                                    response={"error": str(e)}
                                )
                            )
                        )
                
                # Send tool results back to AI
                response = await chat.send_message_async(
                    genai.protos.Content(parts=tool_responses)
                )

            final_reply = response.text

            # 4. SAVE HISTORY
            new_user_msg = {"role": "user", "text": message} # Store original message without context dump to keep it clean
            new_model_msg = {"role": "model", "text": final_reply}
            db_history.append(new_user_msg)
            db_history.append(new_model_msg)
            
            # Keep last 10 messages (5 turns)
            db_history = db_history[-10:]
            
            await phi_db.conversations.update_one(
                {"phone": normalized_phone},
                {"$set": {"messages": db_history, "updated_at": datetime.utcnow()}},
                upsert=True
            )

            return final_reply
        except Exception as e:
            logger.error(f"MASTER_ROUTER_ERROR: {traceback.format_exc()}")
            return "I encountered a clinical error. Please try again."

    async def route_operation(self, args, user_data, user_role, sender_phone):
        op = args.get("operation_type")
        params = args.get("params", "{}")
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                params = {}

        logger.info(f"[ROUTING] {op} for {user_role}")

        # REGISTRATION GROUP
        if "REGISTER" in op:
            return await execute_registration(op, params, user_role, sender_phone)
        
        # PATIENT GROUP
        if op in ["FETCH_HISTORY", "VIEW_RECORDS", "BOOK_TELEHEALTH", "BOOK_APPOINTMENT", "RESCHEDULE_APPOINTMENT", "CANCEL_APPOINTMENT", "PORTAL_LINK"]:
            return await execute_patient_op(op, params, user_data)
        
        # STAFF GROUP
        if op in ["SEARCH_ALL_PATIENTS", "SHIFT_ROSTER", "MANAGE_PATIENTS"]:
            return await execute_staff_op(op, params, user_role)
        
        # MEDICAL GROUP
        if op in ["CHECK_PRESCRIPTIONS", "TRIAGE", "EMERGENCY_TRIAGE", "VOICE_NOTE_TRIAGE"]:
            return await execute_medical_op(op, params, user_role, user_data)
            
        # BILLING GROUP
        if op in ["VIEW_CLAIMS", "REVENUE_SNAPSHOT", "CO_PAY_LINK", "INSURANCE_CHECK"]:
            return await execute_billing_op(op, params, user_role, user_data)

        return {"error": f"Operation {op} routing failed or is not recognized."}

ai_service = AIService()
