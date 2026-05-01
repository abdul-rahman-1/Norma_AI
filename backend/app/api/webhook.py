from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.db.mongodb import get_db
from app.core.security import get_current_user, require_role
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])


# ============================================================================
# CRITICAL: Patient Message Handling
# ============================================================================
# This webhook receives ALL incoming WhatsApp messages.
# We MUST differentiate between staff/doctor messages and patient messages.
# PATIENTS ARE NOT USERS - their messages are logged but NOT processed.
# ============================================================================

async def find_user_by_phone(db, phone: str) -> Optional[dict]:
    """Find a user (staff/doctor/admin) by phone number."""
    user = await db.login_details.find_one({"phone_number": phone})
    return user


async def find_patient_by_phone(db, phone: str) -> Optional[dict]:
    """Find a patient by phone number."""
    patient = await db.patients.find_one({"phone_number": phone})
    return patient


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, db=Depends(get_db)):
    """
    CRITICAL SECURITY ENDPOINT
    
    Receives ALL incoming WhatsApp messages and routes them based on sender:
    - Staff/Doctor messages: Process as commands
    - Patient messages: Log to patient_communications (NO action taken)
    - Unknown: Log as unknown message
    
    This enforces the rule: "PATIENTS ARE NOT SYSTEM USERS"
    """
    try:
        body = await request.form()
        sender_phone = body.get("From", "").replace("whatsapp:", "")
        message_body = body.get("Body", "")
        
        if not sender_phone or not message_body:
            return Response(content="Invalid webhook payload", status_code=400)
        
        logger.info(f"Incoming WhatsApp message from {sender_phone}: {message_body[:50]}...")
        
        # Step 1: Determine sender type
        user = await find_user_by_phone(db, sender_phone)
        patient = await find_patient_by_phone(db, sender_phone)
        
        if user and user.get("role") in ["admin", "doctor", "staff"]:
            # ==============================================================
            # STAFF/DOCTOR MESSAGE - Process as command
            # ==============================================================
            logger.info(f"Command from {user.get('role')}: {sender_phone}")
            
            # Store message for audit trail
            message_record = {
                "phone": sender_phone,
                "sender_type": "staff",
                "sender_id": str(user["_id"]),
                "sender_role": user.get("role"),
                "content": message_body,
                "direction": "inbound",
                "timestamp": datetime.utcnow(),
                "is_read": False,
                "message_type": "command"
            }
            await db.messages.insert_one(message_record)
            
            # Process the command (placeholder - actual implementation in ai_service)
            try:
                response = await ai_service.process_command(
                    user_id=str(user["_id"]),
                    user_role=user.get("role"),
                    message=message_body,
                    db=db
                )
                await whatsapp_service.send_custom_message(sender_phone, response)
            except Exception as e:
                logger.error(f"Command processing failed: {e}")
                error_msg = "Sorry, I couldn't process that command. Please try again."
                await whatsapp_service.send_custom_message(sender_phone, error_msg)
            
            return Response(content="OK", status_code=200)
        
        elif patient:
            # ==============================================================
            # PATIENT MESSAGE - Log only, NO action taken
            # ==============================================================
            logger.info(f"Patient message from {sender_phone} (LOGGED ONLY, NO ACTION)")
            
            # Analyze sentiment (Phase 8.2)
            try:
                sentiment = await ai_service.analyze_sentiment(message_body)
            except Exception as e:
                logger.error(f"Sentiment check failed: {e}")
                sentiment = "neutral"
            
            # CRITICAL: Store in patient_communications but do NOT process
            patient_comm = {
                "patient_id": patient["_id"],
                "phone": sender_phone,
                "message_content": message_body,
                "direction": "inbound",
                "timestamp": datetime.utcnow(),
                "status": "logged",
                "message_type": "patient_message",
                "sentiment": sentiment
            }
            await db.patient_communications.insert_one(patient_comm)
            
            # Send auto-response (no command processing)
            auto_reply = "Your message has been received. A doctor or staff member will contact you soon."
            try:
                await whatsapp_service.send_custom_message(sender_phone, auto_reply)
            except Exception as e:
                logger.error(f"Failed to send auto-reply: {e}")
            
            return Response(content="OK", status_code=200)
        
        else:
            # ==============================================================
            # UNKNOWN SENDER - Log as unknown
            # ==============================================================
            logger.warning(f"Unknown WhatsApp message from {sender_phone}")
            
            unknown_message = {
                "phone": sender_phone,
                "sender_type": "unknown",
                "content": message_body,
                "direction": "inbound",
                "timestamp": datetime.utcnow(),
                "message_type": "unknown"
            }
            await db.unknown_messages.insert_one(unknown_message)
            
            return Response(content="OK", status_code=200)
    
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return Response(content="OK", status_code=200)  # Always return 200 to acknowledge


# ============================================================================
# Staff/Doctor Message Endpoints (Role-Protected)
# ============================================================================

@router.get("/threads")
async def get_message_threads(
    db=Depends(get_db),
    current_user=Depends(require_role("admin", "doctor", "staff"))
):
    """
    Get message threads grouped by phone number.
    Only staff/doctors can access this.
    Shows BOTH staff commands and patient communications for review.
    """
    # Unify messages and patient_communications for the thread list
    pipeline = [
        # First, grab messages from the main messages collection
        {"$project": {
            "phone": 1,
            "content": 1,
            "timestamp": 1,
            "sender_type": 1,
            "is_read": 1
        }},
        # Then union with patient communications
        {"$unionWith": {
            "coll": "patient_communications",
            "pipeline": [
                {"$project": {
                    "phone": 1,
                    "content": "$message_content",
                    "timestamp": 1,
                    "sender_type": {"$literal": "patient"},
                    "is_read": {"$literal": True} # Patient logs are treated as read
                }}
            ]
        }},
        {"$sort": {"timestamp": -1}},
        {
            "$group": {
                "_id": "$phone",
                "last_message": {"$first": "$content"},
                "last_timestamp": {"$first": "$timestamp"},
                "sender_type": {"$first": "$sender_type"},
                "unread_count": {
                    "$sum": {"$cond": [{"$eq": ["$is_read", False]}, 1, 0]}
                }
            }
        },
        {"$sort": {"last_timestamp": -1}}
    ]
    
    threads = await db.messages.aggregate(pipeline).to_list(length=100)
    
    # Enrich with patient/sender names
    for thread in threads:
        if thread["sender_type"] == "staff":
            sender = await db.login_details.find_one({"phone_number": thread["_id"]})
            thread["sender_name"] = sender["name"] if sender else "Unknown Staff"
            thread["type"] = "staff_message"
        elif thread["sender_type"] == "patient":
            patient = await db.patients.find_one({"phone_number": thread["_id"]})
            thread["sender_name"] = patient["full_name"] if patient else "Patient"
            thread["type"] = "patient_message"
        else:
            thread["sender_name"] = "Unknown Sender"
            thread["type"] = "unknown"
            
        # Convert timestamp to ISO string
        if isinstance(thread.get("last_timestamp"), datetime):
            thread["last_timestamp"] = thread["last_timestamp"].isoformat()
        
    return threads


@router.get("/{phone}")
async def get_thread_history(
    phone: str,
    db=Depends(get_db),
    current_user=Depends(require_role("admin", "doctor", "staff"))
):
    """
    Get full message history for a phone number.
    Only staff/doctors can access.
    Combines clinical commands, staff messages, and patient communications.
    """
    # Query both collections
    messages = await db.messages.find({"phone": phone}).to_list(length=100)
    patient_comms = await db.patient_communications.find({"phone": phone}).to_list(length=100)
    
    # Standardize and merge
    unified_history = []
    
    for msg in messages:
        unified_history.append({
            "_id": str(msg["_id"]),
            "content": msg["content"],
            "direction": msg["direction"],
            "timestamp": msg["timestamp"],
            "sender_type": msg.get("sender_type", "unknown")
        })
        
    for comm in patient_comms:
        unified_history.append({
            "_id": str(comm["_id"]),
            "content": comm["message_content"],
            "direction": comm["direction"],
            "timestamp": comm["timestamp"],
            "sender_type": "patient",
            "sentiment": comm.get("sentiment", "neutral")
        })
    
    # Sort by timestamp
    unified_history.sort(key=lambda x: x["timestamp"])
    
    # Mark as read in messages collection
    await db.messages.update_many(
        {"phone": phone, "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    # Convert BSON to JSON serializable
    for msg in unified_history:
        if isinstance(msg.get("timestamp"), datetime):
            msg["timestamp"] = msg["timestamp"].isoformat()
    
    return unified_history


@router.post("/send")
async def send_message(
    phone: str,
    content: str,
    db=Depends(get_db),
    current_user=Depends(require_role("admin", "doctor", "staff"))
):
    """
    Send a WhatsApp message to a phone number.
    
    Only staff/doctors can send.
    Cannot reply to patient messages via this endpoint
    (notifications are automated via notification_service).
    """
    user_role = current_user.get("role", "").lower()
    
    # Store outgoing message for audit trail
    message_obj = {
        "phone": phone,
        "sender_id": str(current_user.get("_id")),
        "sender_role": user_role,
        "content": content,
        "direction": "outbound",
        "timestamp": datetime.utcnow(),
        "is_read": True,
        "message_type": "staff_message"
    }
    result = await db.messages.insert_one(message_obj)
    
    # Send via WhatsApp
    try:
        await whatsapp_service.send_custom_message(phone, content)
        return {"status": "sent", "message_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )
