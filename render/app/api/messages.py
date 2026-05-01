from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.whatsapp_service import whatsapp_service
from app.logger import logger

router = APIRouter(prefix="/api", tags=["messages"])

class SendMessageRequest(BaseModel):
    phone_number: str
    message: str

@router.post("/send-message")
async def send_message(payload: SendMessageRequest):
    """
    Endpoint for internal services (e.g., backend) to send a WhatsApp message.
    """
    try:
        sid = await whatsapp_service.send_custom_message(payload.phone_number, payload.message)
        if sid:
            return {"status": "success", "message_sid": sid}
        else:
            # send_custom_message returns None if failed or disabled
            raise HTTPException(status_code=500, detail="Failed to send message via Twilio.")
    except Exception as e:
        logger.error(f"Error in /send-message endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
