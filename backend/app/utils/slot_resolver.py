"""
Appointment Slot Resolver

Handles doctor availability checking, slot calculation, and conflict detection.
Ensures no double bookings and respects operating hours and breaks.

Key Functions:
- get_available_slots(doctor_id, date) -> List[time]
- is_slot_available(doctor_id, datetime) -> bool
- check_conflict(doctor_id, datetime, duration) -> bool
"""

from datetime import datetime, time, timedelta, date
from typing import List, Tuple, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Standard appointment duration (in minutes)
DEFAULT_APPOINTMENT_DURATION = 30
APPOINTMENT_DURATIONS = {
    "consultation": 30,
    "follow_up": 15,
    "procedure": 60,
    "emergency": 15
}


async def get_operating_hours(db, doctor_id, target_date: date) -> Optional[dict]:
    """
    Fetch doctor's operating hours for a specific day.
    
    Checks:
    1. operating_hours collection for doctor_id + day_of_week
    2. Fallback to doctor document for default hours
    
    Returns:
        {
            'open_time': time(9, 0),
            'close_time': time(17, 0),
            'break_start_time': time(13, 0),
            'break_end_time': time(14, 0)
        }
    """
    # 0=Sunday, 6=Saturday (matches strftime %w)
    day_of_week = int(target_date.strftime("%w"))
    
    # Helper to convert "HH:MM" string or datetime to time object
    def to_time(val):
        if not val: return None
        if isinstance(val, time): return val
        if isinstance(val, datetime): return val.time()
        if isinstance(val, str):
            try:
                h, m = map(int, val.split(':')[:2])
                return time(h, m)
            except: return None
        return None

    # Step 1: Check specific operating hours collection
    hours_doc = await db.operating_hours.find_one({
        "doctor_id": ObjectId(doctor_id),
        "day_of_week": day_of_week,
        "is_open": True
    })
    
    if hours_doc:
        return {
            "open_time": to_time(hours_doc.get("open_time", "09:00")),
            "close_time": to_time(hours_doc.get("close_time", "17:00")),
            "break_start_time": to_time(hours_doc.get("break_start_time")),
            "break_end_time": to_time(hours_doc.get("break_end_time"))
        }

    # Step 2: Fallback to doctor document
    doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id)})
    if not doctor or not doctor.get("is_active"):
        return None
    
    if doctor.get("open_time"):
        return {
            "open_time": to_time(doctor.get("open_time")),
            "close_time": to_time(doctor.get("close_time")),
            "break_start_time": to_time(doctor.get("break_start_time")),
            "break_end_time": to_time(doctor.get("break_end_time"))
        }
    
    # Default fallback (9 AM - 5 PM)
    return {
        "open_time": time(9, 0),
        "close_time": time(17, 0),
        "break_start_time": None,
        "break_end_time": None
    }


async def get_booked_appointments(db, doctor_id: str, target_date: date) -> List[Tuple[time, time]]:
    """
    Get all booked appointments for a doctor on a specific date.
    
    Returns:
        List of (start_time, end_time) tuples for booked slots
    """
    from datetime import datetime as dt
    
    # Create date boundaries
    start_datetime = dt.combine(target_date, time(0, 0))
    end_datetime = dt.combine(target_date, time(23, 59, 59))
    
    appointments = await db.appointments.find({
        "doctor_id": ObjectId(doctor_id),
        "appointment_datetime": {
            "$gte": start_datetime,
            "$lte": end_datetime
        },
        "status": {"$in": ["booked", "confirmed"]}
    }).to_list(length=None)
    
    booked_slots = []
    for apt in appointments:
        apt_dt = apt["appointment_datetime"]
        start = apt_dt.time()
        duration = APPOINTMENT_DURATIONS.get(
            apt.get("appointment_type", "consultation"),
            DEFAULT_APPOINTMENT_DURATION
        )
        end = (
            dt.combine(target_date, start) +
            timedelta(minutes=duration)
        ).time()
        booked_slots.append((start, end))
    
    return booked_slots


def time_in_range(time_value: time, range_start: time, range_end: time) -> bool:
    """Check if a time falls within a range."""
    return range_start <= time_value <= range_end


def time_overlaps(
    start1: time, end1: time,
    start2: time, end2: time
) -> bool:
    """Check if two time ranges overlap."""
    return start1 < end2 and start2 < end1


async def is_slot_available(
    db,
    doctor_id: str,
    appointment_datetime: datetime,
    duration: int = DEFAULT_APPOINTMENT_DURATION
) -> bool:
    """
    Check if a specific slot is available for booking.
    
    Checks:
    1. Doctor is active
    2. Time is within working hours
    3. Time is outside breaks
    4. No existing appointments at that time
    
    Args:
        db: Database connection
        doctor_id: Doctor's ID
        appointment_datetime: Desired appointment datetime
        duration: Appointment duration in minutes
    
    Returns:
        True if slot is available, False otherwise
    """
    target_date = appointment_datetime.date()
    # Get operating hours for this specific day
    hours = await get_operating_hours(db, doctor_id, target_date)
    if not hours:
        logger.warning(f"No operating hours for doctor {doctor_id} on {target_date}")
        return False
    
    slot_start = appointment_datetime.time()
    slot_end = (appointment_datetime + timedelta(minutes=duration)).time()
    
    # Check if within working hours
    if not (hours["open_time"] <= slot_start and slot_end <= hours["close_time"]):
        logger.info(f"Slot {slot_start}-{slot_end} outside working hours {hours['open_time']}-{hours['close_time']}")
        return False
    
    # Check if within break time
    if hours.get("break_start_time") and hours.get("break_end_time"):
        if time_overlaps(slot_start, slot_end, hours["break_start_time"], hours["break_end_time"]):
            logger.info(f"Slot {slot_start}-{slot_end} overlaps with break {hours['break_start_time']}-{hours['break_end_time']}")
            return False
    
    # Check for conflicts with existing appointments
    booked = await get_booked_appointments(db, doctor_id, target_date)
    for booked_start, booked_end in booked:
        if time_overlaps(slot_start, slot_end, booked_start, booked_end):
            logger.info(f"Slot {slot_start}-{slot_end} conflicts with booked slot {booked_start}-{booked_end}")
            return False
    
    logger.info(f"Slot {slot_start}-{slot_end} is available")
    return True


async def get_available_slots(
    db,
    doctor_id: str,
    target_date: date,
    slot_duration: int = 30
) -> List[datetime]:
    """
    Calculate all available appointment slots for a doctor on a specific date.
    """
    # Get operating hours for this specific day
    hours = await get_operating_hours(db, doctor_id, target_date)
    if not hours:
        logger.warning(f"No operating hours defined for doctor {doctor_id} on {target_date}")
        return []
    
    # Get booked appointments
    booked = await get_booked_appointments(db, doctor_id, target_date)
    
    available_slots = []
    
    # Generate all possible slots
    current_time = hours["open_time"]
    close_time = hours["close_time"]
    break_start = hours.get("break_start_time")
    break_end = hours.get("break_end_time")
    
    while current_time < close_time:
        # Calculate slot end time
        slot_end = (
            datetime.combine(target_date, current_time) +
            timedelta(minutes=slot_duration)
        ).time()
        
        # Stop if extends past closing time
        if slot_end > close_time:
            break
        
        # Skip if within break time
        is_break = False
        if break_start and break_end:
            if time_overlaps(current_time, slot_end, break_start, break_end):
                is_break = True
                # Move after break
                current_time = break_end
        
        if is_break:
            continue
        
        # Check if this slot conflicts with booked appointments
        has_conflict = False
        for booked_start, booked_end in booked:
            if time_overlaps(current_time, slot_end, booked_start, booked_end):
                has_conflict = True
                break
        
        # Add slot if no conflicts
        if not has_conflict:
            slot_datetime = datetime.combine(target_date, current_time)
            available_slots.append(slot_datetime)
        
        # Move to next slot
        current_time = (
            datetime.combine(target_date, current_time) +
            timedelta(minutes=slot_duration)
        ).time()
    
    logger.info(f"Found {len(available_slots)} available slots for doctor {doctor_id} on {target_date}")
    return available_slots


async def check_double_booking(
    db,
    doctor_id: str,
    appointment_datetime: datetime,
    duration: int = DEFAULT_APPOINTMENT_DURATION,
    exclude_appointment_id: Optional[str] = None
) -> bool:
    """
    Check if adding an appointment would cause a double booking.
    
    Args:
        db: Database connection
        doctor_id: Doctor's ID
        appointment_datetime: Proposed appointment time
        duration: Appointment duration in minutes
        exclude_appointment_id: Optional appointment ID to exclude (for updates)
    
    Returns:
        True if appointment would cause double booking, False if OK
    """
    target_date = appointment_datetime.date()
    slot_start = appointment_datetime.time()
    slot_end = (appointment_datetime + timedelta(minutes=duration)).time()
    
    query = {
        "doctor_id": ObjectId(doctor_id),
        "appointment_datetime": {
            "$gte": datetime.combine(target_date, time(0, 0)),
            "$lte": datetime.combine(target_date, time(23, 59, 59))
        },
        "status": {"$in": ["booked", "confirmed"]}
    }
    
    if exclude_appointment_id:
        query["_id"] = {"$ne": ObjectId(exclude_appointment_id)}
    
    booked = await get_booked_appointments(db, doctor_id, target_date)
    
    for booked_start, booked_end in booked:
        if time_overlaps(slot_start, slot_end, booked_start, booked_end):
            return True  # Double booking detected
    
    return False  # No double booking


async def get_next_available_slot(
    db,
    doctor_id: str,
    after_datetime: datetime = None
) -> Optional[datetime]:
    """
    Find the next available appointment slot for a doctor.
    
    Searches forward from the given datetime (or now) until an available slot is found.
    
    Args:
        db: Database connection
        doctor_id: Doctor's ID
        after_datetime: Start searching from this time (default: now)
    
    Returns:
        Next available datetime, or None if no slots available in the next 30 days
    """
    if after_datetime is None:
        after_datetime = datetime.now()
    
    # Search for slots in the next 30 days
    for days_ahead in range(30):
        target_date = (after_datetime + timedelta(days=days_ahead)).date()
        slots = await get_available_slots(db, doctor_id, target_date)
        if slots:
            # Filter for slots after the specified time if checking today
            if target_date == after_datetime.date():
                slots = [s for s in slots if s >= after_datetime]
            
            if slots:
                return slots[0]
    
    return None
