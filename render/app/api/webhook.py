from fastapi import APIRouter, Form, Response, BackgroundTasks
from app.services.whatsapp_service import whatsapp_service
from app.services.ai_service import ai_service
import traceback

router = APIRouter()

async def process_and_reply(sender_phone: str, message: str):
    """Background task to handle AI logic and send WhatsApp reply."""
    try:
        print(f"SENTINEL: Background processing started for {sender_phone}")
        response_text = await ai_service.process_message(sender_phone, message)
        await whatsapp_service.send_custom_message(sender_phone, response_text)
        print(f"SENTINEL: Background processing complete for {sender_phone}")
    except Exception as e:
        print(f"SENTINEL BACKGROUND ERROR: {e}")
        traceback.print_exc()

@router.post("/webhook")
async def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Ultra-stable entry point. Responds to Twilio in milliseconds 
    to prevent timeouts (Error 11200) and offloads AI to background.
    """
    try:
        # 1. Sanitize incoming sender phone
        sender_phone = From.replace('whatsapp:', '').strip()
        
        print(f"GATEWAY: Received '{Body}' from {sender_phone}")
        
        # 2. Add AI task to background queue
        background_tasks.add_task(process_and_reply, sender_phone, Body)
        
        # 3. Return a valid empty TwiML instantly
        # This tells Twilio the message was received and closes the connection.
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return Response(content=twiml, media_type="text/xml")
        
    except Exception as e:
        print(f"GATEWAY CRITICAL ERROR: {e}")
        traceback.print_exc()
        # Even on error, return a valid 200 XML to stop Twilio retries/errors
        return Response(content='<Response></Response>', media_type="text/xml")
