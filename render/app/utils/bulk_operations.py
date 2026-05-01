"""
Bulk operation handler for detecting and executing bulk intents.
Handles: "reschedule all", "cancel all", etc.
"""

from typing import Dict, Any, List
from app.db.mongodb import get_phi_db
from bson import ObjectId
import json

async def detect_bulk_intent(user_message: str) -> Dict[str, Any]:
    """
    Detect if user intent is a bulk operation.
    Returns: {"is_bulk": bool, "operation": "reschedule|cancel|etc", "scope": "all|today|this_week"}
    """
    message_lower = user_message.lower()
    
    # Bulk keywords
    if "reschedule all" in message_lower or "reschedule all appointments" in message_lower:
        return {"is_bulk": True, "operation": "reschedule", "scope": "all"}
    
    if "cancel all" in message_lower or "cancel all appointments" in message_lower:
        return {"is_bulk": True, "operation": "cancel", "scope": "all"}
    
    if "delete all" in message_lower:
        return {"is_bulk": True, "operation": "cancel", "scope": "all"}
    
    if "show all" in message_lower or "list all" in message_lower or "all appointments" in message_lower:
        return {"is_bulk": True, "operation": "list", "scope": "all"}
    
    if "today's appointments" in message_lower or "all today" in message_lower:
        return {"is_bulk": True, "operation": "list", "scope": "today"}
    
    if "this week" in message_lower:
        return {"is_bulk": True, "operation": "list", "scope": "week"}
    
    return {"is_bulk": False}


async def get_bulk_appointments(
    doctor_id: str = None, 
    patient_id: str = None, 
    scope: str = "all",
    status: str = None
) -> List[Dict[str, Any]]:
    """
    Fetch appointments for bulk operations.
    Scope: "all", "today", "week"
    """
    from datetime import datetime, timedelta
    
    db = get_phi_db()
    
    try:
        # Build query
        query = {}
        
        if doctor_id:
            try:
                query["doctor_id"] = ObjectId(doctor_id) if isinstance(doctor_id, str) else doctor_id
            except:
                query["doctor_id"] = doctor_id
        
        if patient_id:
            try:
                query["patient_id"] = ObjectId(patient_id) if isinstance(patient_id, str) else patient_id
            except:
                query["patient_id"] = patient_id
        
        if status:
            query["status"] = status
        
        # Date filtering by scope
        now = datetime.utcnow()
        if scope == "today":
            tomorrow = now + timedelta(days=1)
            query["appointment_datetime"] = {
                "$gte": now.replace(hour=0, minute=0, second=0),
                "$lt": tomorrow.replace(hour=0, minute=0, second=0)
            }
        elif scope == "week":
            week_later = now + timedelta(days=7)
            query["appointment_datetime"] = {
                "$gte": now,
                "$lt": week_later
            }
        else:  # "all"
            query["appointment_datetime"] = {"$gte": now}
        
        # Exclude cancelled
        if "status" not in query:
            query["status"] = {"$ne": "cancelled"}
        
        # Fetch with joins
        pipeline = [
            {"$match": query},
            {
                "$lookup": {
                    "from": "patients",
                    "localField": "patient_id",
                    "foreignField": "_id",
                    "as": "patient"
                }
            },
            {"$unwind": {"path": "$patient", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "doctors",
                    "localField": "doctor_id",
                    "foreignField": "_id",
                    "as": "doctor"
                }
            },
            {"$unwind": {"path": "$doctor", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 1,
                    "appointment_datetime": 1,
                    "status": 1,
                    "appointment_type": 1,
                    "patient_name": "$patient.full_name",
                    "doctor_name": "$doctor.full_name"
                }
            },
            {"$sort": {"appointment_datetime": 1}}
        ]
        
        results = await db.appointments.aggregate(pipeline).to_list(length=100)
        return json.loads(json.dumps(results, default=str))
    
    except Exception as e:
        print(f"BULK_APPOINTMENT_ERROR: {e}")
        return []


async def execute_bulk_reschedule(
    appointment_ids: List[str],
    new_datetime: str,
    doctor_id: str = None
) -> Dict[str, Any]:
    """
    Reschedule multiple appointments to new datetime.
    """
    db = get_phi_db()
    
    try:
        from datetime import datetime
        
        # Parse new datetime
        new_dt = datetime.fromisoformat(new_datetime.replace("Z", "+00:00"))
        
        # Convert appointment IDs
        ids = [ObjectId(aid) if isinstance(aid, str) else aid for aid in appointment_ids]
        
        # Reschedule all
        result = await db.appointments.update_many(
            {"_id": {"$in": ids}},
            {
                "$set": {
                    "appointment_datetime": new_dt,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "status": "success",
            "modified_count": result.modified_count,
            "message": f"Rescheduled {result.modified_count} appointments."
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def execute_bulk_cancel(
    appointment_ids: List[str],
    reason: str = "User requested"
) -> Dict[str, Any]:
    """
    Cancel multiple appointments.
    """
    db = get_phi_db()
    
    try:
        from datetime import datetime
        
        ids = [ObjectId(aid) if isinstance(aid, str) else aid for aid in appointment_ids]
        
        result = await db.appointments.update_many(
            {"_id": {"$in": ids}},
            {
                "$set": {
                    "status": "cancelled",
                    "cancellation_reason": reason,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "status": "success",
            "modified_count": result.modified_count,
            "message": f"Cancelled {result.modified_count} appointments."
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}
