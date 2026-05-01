"""
Patient Notification Service

Handles all one-way notifications to patients via WhatsApp.
- Appointment created
- Appointment updated/rescheduled
- Appointment cancelled
- Appointment reminders

CRITICAL: These are ONE-WAY notifications, not interactive communications.
Patients cannot reply with commands (replies are logged only).
"""

from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PatientNotificationService:
    """Service for sending notifications to patients."""
    
    def __init__(self, whatsapp_service, db=None):
        """
        Initialize notification service.
        
        Args:
            whatsapp_service: WhatsApp service instance for sending messages
            db: Database connection (optional, can be injected per method)
        """
        self.whatsapp = whatsapp_service
        self.db = db
    
    async def notify_appointment_created(
        self,
        db,
        patient_id: str,
        doctor_id: str,
        appointment_datetime: datetime,
        appointment_type: str = "consultation"
    ) -> bool:
        """
        Send appointment created notification to patient.
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
            doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
            
            if not patient or not doctor:
                logger.warning(f"Patient or doctor not found: {patient_id}, {doctor_id}")
                return False
            
            phone = patient.get("phone_number")
            if not phone:
                logger.warning(f"Patient {patient_id} has no phone number")
                return False
            
            date_str = appointment_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
            
            message = (
                f"📅 Appointment Confirmed\n\n"
                f"You have a {appointment_type} appointment with\n"
                f"Dr. {doctor.get('full_name', 'N/A')}\n\n"
                f"📍 Date & Time: {date_str}\n"
                f"🏥 Specialty: {doctor.get('specialty', 'N/A')}\n\n"
                f"Please arrive 5-10 minutes early.\n\n"
                f"To reschedule, contact our clinic."
            )
            
            await self.whatsapp.send_custom_message(phone, message)
            
            # Log notification
            await db.patient_communications.insert_one({
                "patient_id": ObjectId(patient_id),
                "phone": phone,
                "direction": "outbound",
                "message_type": "notification_appointment_created",
                "content": message,
                "timestamp": datetime.utcnow(),
                "status": "sent"
            })
            
            logger.info(f"Appointment creation notification sent to {phone}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send appointment creation notification: {e}")
            return False
    
    async def notify_appointment_updated(
        self,
        db,
        patient_id: str,
        doctor_id: str,
        new_appointment_datetime: datetime,
        old_appointment_datetime: Optional[datetime] = None
    ) -> bool:
        """
        Send appointment updated/rescheduled notification to patient.
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
            doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
            
            if not patient or not doctor:
                logger.warning(f"Patient or doctor not found: {patient_id}, {doctor_id}")
                return False
            
            phone = patient.get("phone_number")
            if not phone:
                logger.warning(f"Patient {patient_id} has no phone number")
                return False
            
            new_date_str = new_appointment_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
            
            if old_appointment_datetime:
                old_date_str = old_appointment_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
                message = (
                    f"📅 Appointment Rescheduled\n\n"
                    f"Your appointment with Dr. {doctor.get('full_name', 'N/A')} has been rescheduled.\n\n"
                    f"❌ Previous: {old_date_str}\n"
                    f"✅ New: {new_date_str}\n\n"
                    f"Please update your calendar."
                )
            else:
                message = (
                    f"📅 Appointment Updated\n\n"
                    f"Your appointment with Dr. {doctor.get('full_name', 'N/A')} "
                    f"is confirmed for {new_date_str}."
                )
            
            await self.whatsapp.send_custom_message(phone, message)
            
            # Log notification
            await db.patient_communications.insert_one({
                "patient_id": ObjectId(patient_id),
                "phone": phone,
                "direction": "outbound",
                "message_type": "notification_appointment_updated",
                "content": message,
                "timestamp": datetime.utcnow(),
                "status": "sent"
            })
            
            logger.info(f"Appointment update notification sent to {phone}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send appointment update notification: {e}")
            return False
    
    async def notify_appointment_cancelled(
        self,
        db,
        patient_id: str,
        doctor_id: str,
        cancelled_datetime: datetime,
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """
        Send appointment cancelled notification to patient.
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
            doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
            
            if not patient or not doctor:
                logger.warning(f"Patient or doctor not found: {patient_id}, {doctor_id}")
                return False
            
            phone = patient.get("phone_number")
            if not phone:
                logger.warning(f"Patient {patient_id} has no phone number")
                return False
            
            date_str = cancelled_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
            
            message = (
                f"❌ Appointment Cancelled\n\n"
                f"Your appointment with Dr. {doctor.get('full_name', 'N/A')} "
                f"on {date_str} has been cancelled.\n\n"
            )
            
            if cancellation_reason:
                message += f"Reason: {cancellation_reason}\n\n"
            
            message += "Please contact our clinic to reschedule."
            
            await self.whatsapp.send_custom_message(phone, message)
            
            # Log notification
            await db.patient_communications.insert_one({
                "patient_id": ObjectId(patient_id),
                "phone": phone,
                "direction": "outbound",
                "message_type": "notification_appointment_cancelled",
                "content": message,
                "timestamp": datetime.utcnow(),
                "status": "sent",
                "reason": cancellation_reason
            })
            
            logger.info(f"Appointment cancellation notification sent to {phone}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send appointment cancellation notification: {e}")
            return False
    
    async def notify_appointment_reminder(
        self,
        db,
        patient_id: str,
        doctor_id: str,
        appointment_datetime: datetime,
        hours_before: int = 24
    ) -> bool:
        """
        Send appointment reminder notification to patient.
        
        Args:
            db: Database connection
            patient_id: Patient ID
            doctor_id: Doctor ID
            appointment_datetime: Appointment time
            hours_before: How many hours before the appointment to remind (default 24)
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
            doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
            
            if not patient or not doctor:
                logger.warning(f"Patient or doctor not found: {patient_id}, {doctor_id}")
                return False
            
            phone = patient.get("phone_number")
            if not phone:
                logger.warning(f"Patient {patient_id} has no phone number")
                return False
            
            date_str = appointment_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
            
            message = (
                f"⏰ Appointment Reminder\n\n"
                f"You have an appointment with Dr. {doctor.get('full_name', 'N/A')} "
                f"in {hours_before} hour{'s' if hours_before != 1 else ''}.\n\n"
                f"📍 Time: {date_str}\n\n"
                f"Please arrive 5-10 minutes early.\n"
                f"Reply STOP to opt out of reminders."
            )
            
            await self.whatsapp.send_custom_message(phone, message)
            
            # Log notification
            await db.patient_communications.insert_one({
                "patient_id": ObjectId(patient_id),
                "phone": phone,
                "direction": "outbound",
                "message_type": "notification_appointment_reminder",
                "content": message,
                "timestamp": datetime.utcnow(),
                "status": "sent",
                "hours_before": hours_before
            })
            
            logger.info(f"Appointment reminder sent to {phone}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send appointment reminder: {e}")
            return False
    
    async def notify_custom_message(
        self,
        db,
        patient_id: str,
        message: str,
        message_type: str = "custom"
    ) -> bool:
        """
        Send a custom message to a patient.
        
        Use this for non-standard notifications (medical alerts, lab results, etc).
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            patient = await db.patients.find_one({"_id": ObjectId(patient_id)})
            
            if not patient:
                logger.warning(f"Patient {patient_id} not found")
                return False
            
            phone = patient.get("phone_number")
            if not phone:
                logger.warning(f"Patient {patient_id} has no phone number")
                return False
            
            await self.whatsapp.send_custom_message(phone, message)
            
            # Log notification
            await db.patient_communications.insert_one({
                "patient_id": ObjectId(patient_id),
                "phone": phone,
                "direction": "outbound",
                "message_type": f"notification_{message_type}",
                "content": message,
                "timestamp": datetime.utcnow(),
                "status": "sent"
            })
            
            logger.info(f"Custom message sent to {phone}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send custom message: {e}")
            return False


from app.services.whatsapp_service import whatsapp_service

# Create singleton instance
notification_service = PatientNotificationService(whatsapp_service)
