import json
from datetime import datetime
from app.db.mongodb import get_phi_db

# SCHEMA: { "id", "communication_uuid", "patient_id", "communication_type", "direction", "channel_identifier", "message_content", "media_urls", "ocr_extracted_text", "intent_detected", "norma_response", "sentiment", "timestamp" }

async def handle_patient_communications(op_type, params, user_data=None):
    db = get_phi_db()
    try:
        if op_type == "LOG":
            params["timestamp"] = datetime.utcnow()
            await db.patient_communications.insert_one(params)
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}
