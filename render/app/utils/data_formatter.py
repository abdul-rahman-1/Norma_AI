"""
Data formatting utilities to present user-friendly responses.
Hides internal IDs, formats dates, and structures data for clarity.
"""

from datetime import datetime
from typing import Dict, List, Any

def format_appointment(appt: Dict[str, Any]) -> str:
    """
    Format a single appointment for user-facing display.
    Example output: "Dr. Sarah Smith - Monday, April 30 at 2:30 PM | Type: Consultation | Status: Confirmed"
    """
    dt_str = appt.get("appointment_datetime", "")
    if isinstance(dt_str, str):
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            formatted_date = dt.strftime("%A, %B %d at %I:%M %p")
        except:
            formatted_date = dt_str
    else:
        formatted_date = str(dt_str)
    
    doctor_name = appt.get("doctor_name", "Dr. Unknown")
    patient_name = appt.get("patient_name", "Unknown Patient")
    appt_type = appt.get("appointment_type", "General")
    status = appt.get("status", "Pending").capitalize()
    
    return f"**{doctor_name}** - {formatted_date} | Type: {appt_type} | Status: {status}"


def format_appointments_list(appointments: List[Dict[str, Any]]) -> str:
    """
    Format multiple appointments for display.
    """
    if not appointments:
        return "No appointments found."
    
    formatted = "📋 **Your Appointments:**\n\n"
    for i, appt in enumerate(appointments, 1):
        formatted += f"{i}. {format_appointment(appt)}\n"
    
    return formatted


def format_patient(patient: Dict[str, Any]) -> str:
    """
    Format patient details for user-facing display.
    """
    name = patient.get("full_name", "Unknown")
    phone = patient.get("phone_number", "N/A")
    email = patient.get("email", "N/A")
    dob = patient.get("date_of_birth", "N/A")
    gender = patient.get("gender", "N/A")
    
    return f"**{name}**\n📱 {phone}\n📧 {email}\n🎂 DOB: {dob}\n⚧ Gender: {gender}"


def format_available_slots(slots: List[Dict[str, Any]]) -> str:
    """
    Format available appointment slots.
    """
    if not slots:
        return "No available slots at this time. Please try a different date."
    
    formatted = "✅ **Available Slots:**\n\n"
    for slot in slots:
        dt = slot.get("datetime", "")
        if isinstance(dt, str):
            try:
                dt_obj = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                formatted_dt = dt_obj.strftime("%A, %B %d at %I:%M %p")
            except:
                formatted_dt = dt
        else:
            formatted_dt = str(dt)
        
        formatted += f"• {formatted_dt}\n"
    
    return formatted


def hide_internal_ids(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove internal IDs from data before presenting to user.
    """
    excluded_keys = ["_id", "patient_id", "doctor_id", "appointment_id", "created_by"]
    return {k: v for k, v in data.items() if k not in excluded_keys}


def format_error(error: str, context: str = "") -> str:
    """
    Format error messages for user.
    """
    if "not found" in error.lower():
        return f"❌ Could not find {context}. Please provide more details."
    elif "already" in error.lower():
        return f"⚠️ {context} already exists. Please try a different option."
    else:
        return f"❌ {error}"
