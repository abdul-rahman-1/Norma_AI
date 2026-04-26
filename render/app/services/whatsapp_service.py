from twilio.rest import Client
from app.config import get_settings
from app.logger import logger
from datetime import datetime
import traceback

settings = get_settings()

class WhatsAppService:
    def __init__(self):
        self.client = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            try:
                self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            except Exception as e:
                logger.error(f"TWILIO_INIT_ERROR: {e}")

    async def send_custom_message(self, to_phone: str, body: str):
        """Dispatches a WhatsApp message and logs the clinical interaction."""
        if not self.client:
            logger.warning(f"TWILIO_DISABLED: Could not send to {to_phone}")
            return None

        try:
            # Twilio requires 'whatsapp:' prefix for numbers
            to_formatted = f"whatsapp:{to_phone}" if not to_phone.startswith('whatsapp:') else to_phone
            from_formatted = f"whatsapp:{settings.twilio_phone_number}"

            message = self.client.messages.create(
                from_=from_formatted,
                body=body,
                to=to_formatted
            )
            
            logger.info(f"[WHATSAPP_DISPATCH] SID: {message.sid} | TO: {to_phone}")
            return message.sid
            
        except Exception as e:
            logger.error(f"WHATSAPP_SEND_ERROR to {to_phone}: {traceback.format_exc()}")
            return None

whatsapp_service = WhatsAppService()
