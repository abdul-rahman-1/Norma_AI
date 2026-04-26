from fastapi import APIRouter, Form, Response, BackgroundTasks
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.db.mongodb import get_phi_db
from app.logger import logger
from datetime import datetime
import traceback
import uuid

router = APIRouter()

async def process_and_audit(phone: str, message: str):
    """Handles AI logic, replies to patient, and logs the entire exchange."""
    phi_db = get_phi_db()
    try:
        # Note: Inbound logging is now partially handled inside AIService.process_message 
        # to ensure the prompt and context are tied together.
        
        # 1. Process with AI
        response_text = await ai_service.process_message(phone, message)
        
        # 2. Dispatch WhatsApp Reply
        await whatsapp_service.send_custom_message(phone, response_text)

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
        
        logger.info("\n[INCOMING MESSAGE]")
        logger.info(f"TIME: {timestamp}")
        logger.info(f"FROM: {From}")
        logger.info(f"MESSAGE: \"{Body}\"")
        logger.info(f"SID: {sid}")
        
        if not From or not Body:
            return Response(content="", status_code=200)

        sender_phone = From.replace('whatsapp:', '').strip()
        
        # Dispatch to background audit stream
        background_tasks.add_task(process_and_audit, sender_phone, Body)
        
        # Return empty response to Twilio instantly
        return Response(content="", media_type="text/xml", status_code=200)
        
    except Exception as e:
        logger.error(f"\n[WEBHOOK ERROR] {traceback.format_exc()}")
        return Response(content="", status_code=200)
