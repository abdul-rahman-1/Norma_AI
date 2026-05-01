import google.generativeai as genai
from app.config import get_settings
from app.db.mongodb import get_db
from app.services.whatsapp_service import whatsapp_service
from app.services.notification_service import notification_service
from app.utils.slot_resolver import is_slot_available, get_available_slots
from datetime import datetime, date, timedelta
import json
import uuid
import logging
from bson import ObjectId
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

# ============================================================================
# Clinical Tools Definitions for Gemini
# ============================================================================

def get_patient_details(patient_query: str):
    """
    Search and fetch full details for a patient.
    Args:
        patient_query: Name, Phone Number, or ID of the patient.
    """
    return {"action": "get_patient_details", "query": patient_query}

def list_appointments(doctor_id: str = None, target_date: str = None):
    """
    List appointments for a doctor on a specific date.
    Args:
        doctor_id: Optional ID of the doctor.
        target_date: Optional ISO date (YYYY-MM-DD).
    """
    return {"action": "list_appointments", "doctor_id": doctor_id, "date": target_date}

def get_doctor_availability(doctor_id: str, target_date: str):
    """
    Check for available time slots for a specific doctor.
    Args:
        doctor_id: The ID of the doctor.
        target_date: ISO date (YYYY-MM-DD).
    """
    return {"action": "get_doctor_availability", "doctor_id": doctor_id, "date": target_date}

def create_appointment(patient_id: str, doctor_id: str, datetime_iso: str, appointment_type: str = "consultation"):
    """
    Create a new clinical appointment.
    Args:
        patient_id: The patient's database ID.
        doctor_id: The doctor's database ID.
        datetime_iso: ISO 8601 formatted datetime.
        appointment_type: Type of encounter.
    """
    return {"action": "create_appointment", "patient_id": patient_id, "doctor_id": doctor_id, "time": datetime_iso, "type": appointment_type}

def cancel_appointment(appointment_id: str, reason: str = "Cancelled by clinic"):
    """
    Cancel an existing appointment.
    Args:
        appointment_id: The ID of the appointment to cancel.
        reason: Optional reason for cancellation.
    """
    return {"action": "cancel_appointment", "id": appointment_id, "reason": reason}

def bulk_shift_appointments(doctor_id: str, target_date: str, days_to_shift: int = 1):
    """
    Reschedule all scheduled appointments for a doctor on a specific date by a number of days.
    This informs and notifies all affected patients automatically.
    Args:
        doctor_id: The ID of the doctor.
        target_date: ISO date (YYYY-MM-DD) of the appointments to shift.
        days_to_shift: Number of days to move them forward (default 1).
    """
    return {"action": "bulk_shift", "doctor_id": doctor_id, "date": target_date, "days": days_to_shift}

class AIService:
    """
    AI Assistant for Doctors and Staff.
    Processes natural language commands and executes clinical tools.
    """
    
    def __init__(self):
        # Register tools
        self.tools = [
            get_patient_details,
            list_appointments,
            get_doctor_availability,
            create_appointment,
            cancel_appointment,
            bulk_shift_appointments
        ]
        
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            tools=self.tools
        )
        # Lightweight model for sentiment analysis (no tools needed)
        self.sentiment_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.system_instruction = """
        You are the NORMA AI Clinical Assistant. You assist DOCTORS and STAFF in managing their clinic.
        
        OPERATIONAL PROTOCOLS:
        1. Access the database ONLY via the provided tools.
        2. When a user asks about a patient, search for them first.
        3. Before booking, ALWAYS check doctor availability for the specific date.
        4. When an action is performed, provide a clear confirmation.
        5. You are an INTERNAL tool. Never assume you are talking to a patient.
        6. Always use IDs when calling tools.
        9. If a user asks to "Reschedule all shifts" or "Move everything for today to tomorrow", use the bulk_shift_appointments tool.
        
        Current Year: 2026.
        """

    async def analyze_sentiment(self, message: str) -> str:
        """Analyze the sentiment of a patient message."""
        try:
            prompt = f"Analyze the sentiment of the following patient message. Reply ONLY with one word: 'positive', 'neutral', 'negative', or 'urgent'. Message: '{message}'"
            response = await self.sentiment_model.generate_content_async(prompt)
            result = response.text.strip().lower()
            if result not in ['positive', 'neutral', 'negative', 'urgent']:
                return 'neutral'
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return "neutral"

    async def process_command(self, user_id: str, user_role: str, message: str, db) -> str:
        """
        Process a natural language command from a staff member or doctor.
        Uses manual function calling so execute_tool_call() actually runs DB mutations.
        """
        # Fetch relevant context
        doctors = await db.doctors.find({"is_active": True}).to_list(length=10)
        doc_info = "\n".join([f"- {d['full_name']} (ID: {str(d['_id'])}, Specialty: {d['specialty']})" for d in doctors])
        
        # [NEW] Fetch relevant knowledge context (RAG)
        from app.services.knowledge.knowledge_retriever import retrieve_context
        knowledge_context = await retrieve_context(message, db)

        accessible_info = f"Current User Role: {user_role}\nAvailable Doctors:\n{doc_info}"

        context_prompt = f"""
        {self.system_instruction}

        CLINIC KNOWLEDGE BASE (Use this to answer policies/rules questions):
        {knowledge_context if knowledge_context else "No specific documents found. Reply based on general logic or ask for clarification."}

        COMMAND CONTEXT:
        {accessible_info}
        Current Time: {datetime.utcnow().isoformat()}

        STAFF COMMAND: "{message}"
        """

        try:
            # Manual function calling — disable automatic so we control execution
            chat = self.model.start_chat(enable_automatic_function_calling=False)
            response = chat.send_message(context_prompt)

            # Tool call loop: intercept Gemini function calls and execute them ourselves
            max_iterations = 5
            for _ in range(max_iterations):
                # Check if Gemini wants to call a tool
                has_function_call = False
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call.name:
                        has_function_call = True
                        fc = part.function_call
                        tool_name = fc.name
                        tool_args = dict(fc.args)

                        logger.info(f"Gemini calling tool: {tool_name} with args: {tool_args}")

                        # Execute the actual DB operation
                        result = await self.execute_tool_call(tool_name, tool_args, db, user_id, user_role)

                        # Feed the real result back to Gemini
                        import google.generativeai.protos as protos
                        response = chat.send_message(
                            protos.Part(
                                function_response=protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": str(result)}
                                )
                            )
                        )
                        break

                if not has_function_call:
                    # No more tool calls — return the final text response
                    break

            return response.text

        except Exception as e:
            logger.error(f"AI command processing error: {e}")
            return "I encountered an error while processing your request. Please try again or use a simpler command."

    async def execute_tool_call(self, name: str, args: dict, db, user_id: str = None, user_role: str = None) -> Any:
        """
        Execute the actual database operations triggered by Gemini tools.
        """
        logger.info(f"AI EXECUTION: {name} with args {args}")
        
        if name == "get_patient_details":
            query = args.get("patient_query")
            patient = await db.patients.find_one({
                "$or": [
                    {"full_name": {"$regex": query, "$options": "i"}},
                    {"phone_number": {"$regex": query, "$options": "i"}}
                ]
            })
            if patient:
                patient["_id"] = str(patient["_id"])
                return patient
            return {"error": "Patient not found"}

        elif name == "list_appointments":
            doc_id = args.get("doctor_id")
            target_date = args.get("date")

            query = {}
            if doc_id:
                query["doctor_id"] = ObjectId(doc_id)
            if target_date:
                dt_start = datetime.fromisoformat(target_date).replace(hour=0, minute=0)
                dt_end = dt_start + timedelta(days=1)
                query["appointment_datetime"] = {"$gte": dt_start, "$lt": dt_end}

            pipeline = [
                {"$match": query},
                {"$lookup": {"from": "patients", "localField": "patient_id", "foreignField": "_id", "as": "patient"}},
                {"$unwind": {"path": "$patient", "preserveNullAndEmptyArrays": True}},
                {"$lookup": {"from": "doctors", "localField": "doctor_id", "foreignField": "_id", "as": "doctor"}},
                {"$unwind": {"path": "$doctor", "preserveNullAndEmptyArrays": True}},
                {"$project": {
                    "_id": {"$toString": "$_id"},
                    "patient_name": "$patient.full_name",
                    "patient_phone": "$patient.phone_number",
                    "doctor_name": "$doctor.full_name",
                    "appointment_datetime": 1,
                    "status": 1,
                    "appointment_type": 1
                }},
                {"$limit": 20}
            ]
            appointments = await db.appointments.aggregate(pipeline).to_list(None)
            for apt in appointments:
                if hasattr(apt.get("appointment_datetime"), "isoformat"):
                    apt["appointment_datetime"] = apt["appointment_datetime"].isoformat()
            return appointments

        elif name == "get_doctor_availability":
            doc_id = args.get("doctor_id")
            target_date = args.get("date")
            if not doc_id or not target_date:
                return {"error": "Doctor ID and Date are required"}
                
            try:
                dt_date = date.fromisoformat(target_date)
                slots = await get_available_slots(db, doc_id, dt_date)
                return [s.isoformat() for s in slots]
            except Exception as e:
                return {"error": str(e)}

        elif name == "create_appointment":
            doc_id = args.get("doctor_id")
            patient_id = args.get("patient_id")
            apt_time = datetime.fromisoformat(args.get("time").replace('Z', ''))
            
            is_avail = await is_slot_available(db, doc_id, apt_time)
            if not is_avail:
                return {"error": "Slot is no longer available"}
                
            new_apt = {
                "patient_id": ObjectId(patient_id),
                "doctor_id": ObjectId(doc_id),
                "appointment_datetime": apt_time,
                "status": "booked",
                "appointment_type": args.get("type", "consultation"),
                "created_at": datetime.utcnow()
            }
            result = await db.appointments.insert_one(new_apt)
            
            await notification_service.notify_appointment_created(
                db, patient_id, doc_id, apt_time, args.get("type", "consultation")
            )
            
            return {"status": "success", "id": str(result.inserted_id)}

        elif name == "cancel_appointment":
            apt_id = args.get("id")
            apt = await db.appointments.find_one({"_id": ObjectId(apt_id)})
            if not apt:
                return {"error": "Appointment not found"}
                
            await db.appointments.delete_one({"_id": ObjectId(apt_id)})
            
            await notification_service.notify_appointment_cancelled(
                db, str(apt["patient_id"]), str(apt["doctor_id"]), 
                apt["appointment_datetime"], args.get("reason")
            )
            
            return {"status": "success"}

        elif name == "bulk_shift_appointments":
            # [NEW] Execute Action B24 from render microservice
            try:
                import sys
                import os
                import importlib
                
                # Add render to sys.path
                CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
                RENDER_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "..", "render"))
                if RENDER_PATH not in sys.path:
                    sys.path.append(RENDER_PATH)
                
                module = importlib.import_module("app.features.clinical_features.B24_bulk_shift")
                
                params = {
                    "doctor_id": args.get("doctor_id"),
                    "date": args.get("target_date") or args.get("date"),
                    "days": int(args.get("days_to_shift") or args.get("days") or 1)
                }
                
                user_data = {"_id": user_id} if user_id else {}
                
                result = await module.execute(
                    params=params,
                    user_role=user_role.upper() if user_role else "DOCTOR",
                    user_data=user_data
                )
                return result
            except Exception as e:
                logger.error(f"Bulk shift tool error: {e}")
                return {"error": str(e)}

        return {"error": f"Tool {name} not implemented"}

ai_service = AIService()
