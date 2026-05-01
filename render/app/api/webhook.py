from fastapi import APIRouter, Form, Response, BackgroundTasks
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
from app.db.mongodb import get_phi_db
from app.logger import logger
from datetime import datetime
import traceback
import uuid

router = APIRouter()

async def process_and_audit(phone: str, message: str, media_url: str = None, media_type: str = None):
    """Handles AI logic, replies to patient, and logs the entire exchange."""
    try:
        # 1. Process with AI (now handles media)
        response_text = await ai_service.process_message(phone, message, media_url, media_type)
        
        # 2. Dispatch WhatsApp Reply
        await whatsapp_service.send_custom_message(phone, response_text)

    except Exception as e:
        logger.error(f"[PROCESS_AND_AUDIT ERROR] Phone: {phone} | Error: {traceback.format_exc()}")

@router.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(None),
    From: str = Form(None),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None),
    MessageSid: str = Form(None)
):
    """Gateway entry point. Detects Text and Voice Notes."""
    try:
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        logger.info("\n[INCOMING MESSAGE]")
        logger.info(f"FROM: {From}")
        if Body: logger.info(f"TEXT: \"{Body}\"")
        if MediaUrl0: logger.info(f"VOICE NOTE: {MediaUrl0} ({MediaContentType0})")
        
        if not From:
            return Response(content="", status_code=200)

        sender_phone = From.replace('whatsapp:', '').strip()
        
        # Dispatch to background with potential media
        background_tasks.add_task(process_and_audit, sender_phone, Body or "", MediaUrl0, MediaContentType0)
        
        return Response(content="", media_type="text/xml", status_code=200)
        
    except Exception as e:
        logger.error(f"\n[WEBHOOK ERROR] {traceback.format_exc()}")
        return Response(content="", status_code=200)
