"""
Slot resolution: Automatically compute next available slots for doctors.
Uses doctors, operating_hours, and appointments collections.
"""

from datetime import datetime, timedelta
from app.db.mongodb import get_phi_db
from typing import List, Dict, Any
from bson import ObjectId
import json

async def get_next_available_slots(doctor_id: str, num_slots: int = 3) -> List[Dict[str, Any]]:
    """
    Compute next available slots for a doctor based on:
    - Doctor's operating hours
    - Existing appointments
    - Slot duration (typically 30-60 minutes)
    
    Returns list of available datetime slots.
    """
    db = get_phi_db()
    
    try:
        # Convert doctor_id to ObjectId if needed
        if isinstance(doctor_id, str):
            try:
                doctor_id = ObjectId(doctor_id)
            except:
                pass
        
        # Get doctor details and operating hours
        doctor = await db.doctors.find_one({"_id": doctor_id})
        if not doctor:
            return []
        
        operating_hours = doctor.get("operating_hours", {})
        if not operating_hours:
            # Default: 9 AM - 5 PM, Mon-Fri
            operating_hours = {
                "Monday": {"start": "09:00", "end": "17:00"},
                "Tuesday": {"start": "09:00", "end": "17:00"},
                "Wednesday": {"start": "09:00", "end": "17:00"},
                "Thursday": {"start": "09:00", "end": "17:00"},
                "Friday": {"start": "09:00", "end": "17:00"},
            }
        
        # Get existing appointments for this doctor in next 30 days
        now = datetime.utcnow()
        future_date = now + timedelta(days=30)
        
        existing = await db.appointments.find({
            "doctor_id": doctor_id,
            "appointment_datetime": {
                "$gte": now,
                "$lte": future_date
            },
            "status": {"$ne": "cancelled"}
        }).to_list(length=100)
        
        # Extract booked times
        booked_times = set()
        for appt in existing:
            dt = appt.get("appointment_datetime")
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            booked_times.add(dt)
        
        # Generate available slots
        available_slots = []
        current = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Move to next day if already past operating hours
        if current.hour >= 17:
            current += timedelta(days=1)
        
        while len(available_slots) < num_slots and current <= future_date:
            day_name = current.strftime("%A")
            
            # Check if doctor works this day
            if day_name in operating_hours:
                hours = operating_hours[day_name]
                start_hour = int(hours["start"].split(":")[0])
                end_hour = int(hours["end"].split(":")[0])
                
                # Move to start of operating hours if before
                if current.hour < start_hour:
                    current = current.replace(hour=start_hour, minute=0)
                
                # Generate 30-minute slots throughout the day
                while current.hour < end_hour and len(available_slots) < num_slots:
                    if current not in booked_times:
                        available_slots.append({
                            "datetime": current.isoformat(),
                            "formatted": current.strftime("%A, %B %d at %I:%M %p")
                        })
                    
                    current += timedelta(minutes=30)
            
            # Move to next day
            current = current.replace(hour=9, minute=0) + timedelta(days=1)
        
        return available_slots
    
    except Exception as e:
        return []


async def get_slots_for_date(doctor_id: str, target_date: str) -> List[Dict[str, Any]]:
    """
    Get available slots for a specific date.
    target_date format: "2026-04-30"
    """
    db = get_phi_db()
    
    try:
        if isinstance(doctor_id, str):
            try:
                doctor_id = ObjectId(doctor_id)
            except:
                pass
        
        # Parse target date
        target = datetime.strptime(target_date, "%Y-%m-%d")
        
        doctor = await db.doctors.find_one({"_id": doctor_id})
        if not doctor:
            return []
        
        operating_hours = doctor.get("operating_hours", {})
        day_name = target.strftime("%A")
        
        if day_name not in operating_hours:
            return []  # Doctor doesn't work this day
        
        hours = operating_hours[day_name]
        start_hour = int(hours["start"].split(":")[0])
        end_hour = int(hours["end"].split(":")[0])
        
        # Get existing appointments for this date
        existing = await db.appointments.find({
            "doctor_id": doctor_id,
            "appointment_datetime": {
                "$gte": target,
                "$lt": target + timedelta(days=1)
            },
            "status": {"$ne": "cancelled"}
        }).to_list(length=100)
        
        booked_times = set()
        for appt in existing:
            dt = appt.get("appointment_datetime")
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            booked_times.add(dt)
        
        # Generate slots
        available_slots = []
        current = target.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        while current.hour < end_hour:
            if current not in booked_times:
                available_slots.append({
                    "datetime": current.isoformat(),
                    "formatted": current.strftime("%I:%M %p")
                })
            
            current += timedelta(minutes=30)
        
        return available_slots
    
    except Exception as e:
        return []
