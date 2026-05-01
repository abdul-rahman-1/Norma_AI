import json
from app.services.whatsapp_service import whatsapp_service

async def execute_surgical_prep(params, user_role, user_data=None):
    """Action B35: Send pre-op instructions."""
    msg = "📋 *Surgical Preparation*\n3 days to your surgery: Please stop taking Aspirin or any blood thinners."
    await whatsapp_service.send_custom_message(user_data["phone_number"], msg)
    return {"status": "success", "message": "Pre-op instructions sent."}
