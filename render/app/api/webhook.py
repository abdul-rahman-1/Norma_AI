from fastapi import APIRouter, Form, Response, BackgroundTasks
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.db.mongodb import get_db
from app.logger import logger
from datetime import datetime
import traceback
import sys

router = APIRouter()

def flush_print(msg):
    print(msg)
    sys.stdout.flush()

async def process_and_audit(phone: str, message: str):
    """Handles AI logic, replies to patient, and logs the entire exchange."""
    flush_print(f"\n--- NEW INBOUND MESSAGE ---")
    flush_print(f"SENDER: {phone}")
    flush_print(f"MESSAGE: {message}")
    
    db = get_db()
    try:
        # 1. Log Inbound Message
        if db is not None:
            await db.messages.insert_one({
                "phone": phone,
                "direction": "inbound",
                "text": message,
                "timestamp": datetime.utcnow()
            })
        else:
            flush_print("CRITICAL: MongoDB connection is NULL in process_and_audit")

        # 2. Process with AI
        flush_print(f"AI_SERVICE: Calling process_message for {phone}...")
        response_text = await ai_service.process_message(phone, message)
        flush_print(f"AI_SERVICE: Response generated: '{response_text[:50]}...'")
        
        # 3. Dispatch WhatsApp Reply
        flush_print(f"TWILIO: Dispatching message to {phone}...")
        await whatsapp_service.send_custom_message(phone, response_text)

        # 4. Log Outbound Response
        if db is not None:
            await db.messages.insert_one({
                "phone": phone,
                "direction": "outbound",
                "text": response_text,
                "timestamp": datetime.utcnow()
            })
        flush_print(f"--- MESSAGE CYCLE COMPLETE ---\n")

    except Exception as e:
        flush_print(f"WH_PROCESSOR_ERROR: {str(e)}")
        flush_print(traceback.format_exc())

@router.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(...),
    From: str = Form(...)
):
    """Gateway entry point. Responds to Twilio instantly and audits in background."""
    try:
        sender_phone = From.replace('whatsapp:', '').strip()
        flush_print(f"GATEWAY: Received webhook from {sender_phone}")
        
        # Dispatch to background audit stream
        background_tasks.add_task(process_and_audit, sender_phone, Body)
        
        # Return empty response to Twilio to prevent automatic "OK" replies
        return Response(content="", media_type="text/xml", status_code=200)
        
    except Exception as e:
        flush_print(f"GATEWAY_WEBHOOK_EXCEPTION: {e}")
        return Response(content="", status_code=200)
