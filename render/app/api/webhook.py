from fastapi import APIRouter, Form, Response, BackgroundTasks
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.db.mongodb import get_db
from app.logger import logger
from datetime import datetime
import traceback
import sys

router = APIRouter()

async def process_and_audit(phone: str, message: str):
    """Handles AI logic, replies to patient, and logs the entire exchange."""
    db = get_db()
    try:
        # 1. Log Inbound Message to DB
        if db is not None:
            await db.messages.insert_one({
                "phone": phone,
                "direction": "inbound",
                "text": message,
                "timestamp": datetime.utcnow()
            })
        
        # 2. Process with AI
        response_text = await ai_service.process_message(phone, message)
        
        # 3. Dispatch WhatsApp Reply (Logging happens inside send_custom_message)
        await whatsapp_service.send_custom_message(phone, response_text)

        # 4. Log Outbound Response to DB
        if db is not None:
            await db.messages.insert_one({
                "phone": phone,
                "direction": "outbound",
                "text": response_text,
                "timestamp": datetime.utcnow()
            })

    except Exception as e:
        logger.error(f"[PROCESS_AND_AUDIT ERROR] Phone: {phone} | Error: {traceback.format_exc()}")

@router.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(None),
    From: str = Form(None),
    To: str = Form(None),
    MessageSid: str = Form(None),
    SmsSid: str = Form(None)
):
    """Gateway entry point. Responds to Twilio instantly and audits in background."""
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        sid = MessageSid or SmsSid or "Unknown"
        
        # Structured logging per @fix.md
        logger.info("\n[INCOMING MESSAGE]")
        logger.info(f"TIME: {timestamp}")
        logger.info(f"FROM: {From}")
        logger.info(f"TO: {To}")
        logger.info(f"MESSAGE: \"{Body}\"")
        logger.info(f"SID: {sid}")
        
        if not From or not Body:
            logger.warning("GATEWAY: Received partial Twilio request (missing From or Body)")
            return Response(content="", status_code=200)

        sender_phone = From.replace('whatsapp:', '').strip()
        
        # Dispatch to background audit stream
        background_tasks.add_task(process_and_audit, sender_phone, Body)
        
        # Return empty response to Twilio
        return Response(content="", media_type="text/xml", status_code=200)
        
    except Exception as e:
        timestamp = datetime.utcnow().isoformat() + "Z"
        logger.error(f"\n[ERROR]")
        logger.error(f"TIME: {timestamp}")
        logger.error(f"ERROR: {traceback.format_exc()}")
        return Response(content="", status_code=200)
