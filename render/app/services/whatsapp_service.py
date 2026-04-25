from twilio.rest import Client
from app.config import get_settings
from app.logger import logger
from datetime import datetime
import logging
import sys

settings = get_settings()

class WhatsAppService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = f"whatsapp:{settings.twilio_phone_number}"

    async def send_custom_message(self, to_phone: str, body: str):
        try:
            # 1. Truncate to prevent Twilio Error 21617 (Message too long)
            safe_body = body[:1500] if len(body) > 1500 else body

            # 2. Clean number (remove spaces, dashes)
            clean_phone = to_phone.strip().replace(" ", "").replace("-", "")
            
            # 2. Enforce E.164 (ensure it starts with +)
            if not clean_phone.startswith('+'):
                clean_phone = f"+{clean_phone}"

            to_whatsapp = f"whatsapp:{clean_phone}"
            
            # Log outgoing message per @fix.md
            timestamp = datetime.utcnow().isoformat() + "Z"
            logger.info("\n[OUTGOING MESSAGE]")
            logger.info(f"TIME: {timestamp}")
            logger.info(f"TO: {to_whatsapp}")
            logger.info(f"FROM: {self.from_number}")
            logger.info(f"RESPONSE: \"{safe_body}\"")
            
            message = self.client.messages.create(
                body=safe_body, 
                from_=self.from_number, 
                to=to_whatsapp
            )
            return message.sid
        except Exception as e:
            timestamp = datetime.utcnow().isoformat() + "Z"
            logger.error(f"\n[ERROR - OUTGOING]")
            logger.error(f"TIME: {timestamp}")
            logger.error(f"TO: {to_phone}")
            logger.error(f"ERROR: {e}")
            return None

whatsapp_service = WhatsAppService()
