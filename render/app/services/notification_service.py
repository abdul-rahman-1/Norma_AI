"""
NotificationService: One-way patient notifications for appointment changes.
Patients are NOT active users - they only receive notifications.
"""

from typing import Dict, Any, Optional
from app.db.mongodb import get_phi_db
from app.logger import logger
from datetime import datetime
import httpx
from app.config import get_settings

settings = get_settings()

class NotificationService:
    """
    Sends one-way WhatsApp notifications to patients.
    This is NOT a chatbot - patients cannot respond and control flow.
    """
    
    @staticmethod
    async def notify_appointment_created(
        patient_phone: str,
        patient_name: str,
        doctor_name: str,
        appointment_datetime: str,
        appointment_type: str
    ) -> bool:
        """Send appointment creation notification."""
        message = f"""
Hi {patient_name},

Your appointment has been confirmed:

📅 Date & Time: {appointment_datetime}
👨‍⚕️ Doctor: {doctor_name}
📝 Type: {appointment_type}

Please arrive 10 minutes early.

— Norma AI Health System
        """.strip()
        
        return await NotificationService._send_whatsapp_message(patient_phone, message)
    
    @staticmethod
    async def notify_appointment_rescheduled(
        patient_phone: str,
        patient_name: str,
        doctor_name: str,
        old_datetime: str,
        new_datetime: str
    ) -> bool:
        """Send appointment rescheduling notification."""
        message = f"""
Hi {patient_name},

Your appointment with {doctor_name} has been rescheduled:

❌ Old: {old_datetime}
✅ New: {new_datetime}

Please confirm if this works for you, or contact us to reschedule again.

— Norma AI Health System
        """.strip()
        
        return await NotificationService._send_whatsapp_message(patient_phone, message)
    
    @staticmethod
    async def notify_appointment_cancelled(
        patient_phone: str,
        patient_name: str,
        doctor_name: str,
        appointment_datetime: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send appointment cancellation notification."""
        reason_text = f"\nReason: {reason}" if reason else ""
        
        message = f"""
Hi {patient_name},

Your appointment with {doctor_name} on {appointment_datetime} has been cancelled.{reason_text}

Please contact us if you'd like to reschedule.

— Norma AI Health System
        """.strip()
        
        return await NotificationService._send_whatsapp_message(patient_phone, message)
    
    @staticmethod
    async def notify_prescription_ready(
        patient_phone: str,
        patient_name: str,
        pharmacy_name: str,
        medications_count: int
    ) -> bool:
        """Send prescription ready notification."""
        message = f"""
Hi {patient_name},

Your prescription is ready for pickup!

📍 Pharmacy: {pharmacy_name}
💊 Medications: {medications_count}

Please visit at your earliest convenience.

— Norma AI Health System
        """.strip()
        
        return await NotificationService._send_whatsapp_message(patient_phone, message)
    
    @staticmethod
    async def notify_lab_results_available(
        patient_phone: str,
        patient_name: str,
        test_name: str
    ) -> bool:
        """Send lab results available notification."""
        message = f"""
Hi {patient_name},

Your lab results for {test_name} are now available.

Please contact your doctor for consultation.

— Norma AI Health System
        """.strip()
        
        return await NotificationService._send_whatsapp_message(patient_phone, message)
    
    @staticmethod
    async def _send_whatsapp_message(recipient_phone: str, message: str) -> bool:
        """
        Internal: Send WhatsApp message via Twilio.
        This is ONE-WAY only - for notifications, not conversation.
        """
        try:
            from twilio.rest import Client
            
            client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
            
            msg = client.messages.create(
                from_=settings.whatsapp_number,
                body=message,
                to=f"whatsapp:{recipient_phone}"
            )
            
            logger.info(f"[NOTIFICATION] Sent to {recipient_phone} | SID: {msg.sid}")
            return True
        
        except Exception as e:
            logger.error(f"[NOTIFICATION_ERROR] Failed to send to {recipient_phone}: {str(e)}")
            return False
    
    @staticmethod
    async def log_notification(
        patient_phone: str,
        notification_type: str,
        message: str,
        status: str = "sent"
    ):
        """Log notification in database for audit."""
        try:
            phi_db = get_phi_db()
            
            await phi_db.notifications.insert_one({
                "patient_phone": patient_phone,
                "notification_type": notification_type,
                "message": message,
                "status": status,
                "sent_at": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"[NOTIFICATION_LOG_ERROR]: {str(e)}")

notification_service = NotificationService()
