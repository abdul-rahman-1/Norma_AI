"""
validators.py
-------------
Per-entity, per-row field validation.
Returns a list of RowError objects — never raises, always collects all errors
so the preview response has a complete picture.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RowError:
    row: int
    field: str
    reason: str


# ---------------------------------------------------------------------------
# Shared validators (reusable primitives)
# ---------------------------------------------------------------------------

_E164_RE = re.compile(r"^\+?[1-9]\d{6,14}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_TIME_RE  = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")

VALID_GENDERS   = {"male", "female", "other", "prefer not to say"}
VALID_APT_STATUSES = {"booked", "rescheduled", "canceled", "completed", "pending"}
VALID_DAYS      = set(range(7))   # 0 = Sunday … 6 = Saturday


def _phone(val, row: int, field_name: str) -> Optional[RowError]:
    if not val:
        return RowError(row, field_name, "Phone number is required")
    clean = str(val).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not _E164_RE.match(clean):
        return RowError(row, field_name, f"Invalid phone format: '{val}'. Use E.164 (+XXXXXXXXXX) or 10 digits.")
    return None


def _email(val, row: int, field_name: str) -> Optional[RowError]:
    if not val:
        return None  # email is always optional
    if not _EMAIL_RE.match(str(val).strip()):
        return RowError(row, field_name, f"Invalid email format: '{val}'")
    return None


def _nonempty(val, row: int, field_name: str) -> Optional[RowError]:
    if val is None or str(val).strip() == "" or str(val).strip().lower() == "nan":
        return RowError(row, field_name, f"'{field_name}' is required and cannot be empty")
    return None


def _date(val, row: int, field_name: str, future_only: bool = False) -> Optional[RowError]:
    if not val:
        return None
    try:
        if isinstance(val, datetime):
            dt = val
        else:
            dt = datetime.fromisoformat(str(val).strip())
        if future_only and dt < datetime.utcnow():
            return RowError(row, field_name, f"'{field_name}' must be a future date/time (got '{val}')")
    except (ValueError, TypeError):
        return RowError(row, field_name, f"'{field_name}' is not a valid date/time: '{val}'")
    return None


def _time(val, row: int, field_name: str) -> Optional[RowError]:
    if not val:
        return None
    if not _TIME_RE.match(str(val).strip()):
        return RowError(row, field_name, f"'{field_name}' must be HH:MM format, got '{val}'")
    return None


def _choice(val, row: int, field_name: str, choices: set) -> Optional[RowError]:
    if not val:
        return None
    if str(val).strip().lower() not in choices:
        return RowError(row, field_name, f"'{field_name}' must be one of {choices}, got '{val}'")
    return None


# ---------------------------------------------------------------------------
# Per-entity validators
# ---------------------------------------------------------------------------

def validate_patient(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("full_name"), row, "full_name"))
    errs.append(_phone(record.get("phone_number") or record.get("phone"), row, "phone_number"))
    errs.append(_email(record.get("email"), row, "email"))
    errs.append(_date(record.get("date_of_birth"), row, "date_of_birth"))
    errs.append(_choice(record.get("gender"), row, "gender", VALID_GENDERS))
    return [e for e in errs if e]


def validate_doctor(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("full_name"), row, "full_name"))
    errs.append(_phone(record.get("whatsapp_number"), row, "whatsapp_number"))
    errs.append(_email(record.get("email"), row, "email"))
    fee = record.get("consultation_fee")
    if fee is not None:
        try:
            float(fee)
        except (ValueError, TypeError):
            errs.append(RowError(row, "consultation_fee", f"Must be a number, got '{fee}'"))
    return [e for e in errs if e]


def validate_staff(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("full_name"), row, "full_name"))
    errs.append(_phone(record.get("phone_number") or record.get("phone"), row, "phone_number"))
    errs.append(_email(record.get("email"), row, "email"))
    return [e for e in errs if e]


def validate_appointment(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("patient_phone") or record.get("patient_id"), row, "patient_phone"))
    errs.append(_nonempty(record.get("doctor_phone") or record.get("doctor_id"), row, "doctor_phone"))
    errs.append(_date(record.get("appointment_datetime") or record.get("scheduled_at"), row, "appointment_datetime", future_only=False))
    if not (record.get("appointment_datetime") or record.get("scheduled_at")):
        errs.append(RowError(row, "appointment_datetime", "appointment_datetime is required"))
    errs.append(_choice(record.get("status"), row, "status", VALID_APT_STATUSES))
    return [e for e in errs if e]


def validate_prescription(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("patient_phone") or record.get("patient_id"), row, "patient_phone"))
    errs.append(_nonempty(record.get("medication_name") or record.get("medication"), row, "medication_name"))
    errs.append(_date(record.get("start_date"), row, "start_date"))
    errs.append(_date(record.get("end_date"), row, "end_date"))
    return [e for e in errs if e]


def validate_medical_record(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("patient_phone") or record.get("patient_id"), row, "patient_phone"))
    errs.append(_nonempty(record.get("record_type"), row, "record_type"))
    errs.append(_date(record.get("visit_date"), row, "visit_date"))
    return [e for e in errs if e]


def validate_clinic_info(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("key"), row, "key"))
    errs.append(_nonempty(record.get("value"), row, "value"))
    return [e for e in errs if e]


def validate_operating_hours(record: dict, row: int) -> list[RowError]:
    errs = []
    day = record.get("day_of_week")
    if day is None:
        errs.append(RowError(row, "day_of_week", "day_of_week is required (0=Sunday ... 6=Saturday)"))
    else:
        try:
            if int(day) not in VALID_DAYS:
                raise ValueError()
        except (ValueError, TypeError):
            errs.append(RowError(row, "day_of_week", f"day_of_week must be 0–6, got '{day}'"))
    errs.append(_time(record.get("open_time"), row, "open_time"))
    errs.append(_time(record.get("close_time"), row, "close_time"))
    errs.append(_time(record.get("break_start_time"), row, "break_start_time"))
    errs.append(_time(record.get("break_end_time"), row, "break_end_time"))
    return [e for e in errs if e]


def validate_insurance_claim(record: dict, row: int) -> list[RowError]:
    errs = []
    errs.append(_nonempty(record.get("patient_phone") or record.get("patient_id"), row, "patient_phone"))
    errs.append(_nonempty(record.get("claim_number"), row, "claim_number"))
    errs.append(_nonempty(record.get("provider"), row, "provider"))
    errs.append(_date(record.get("submitted_date"), row, "submitted_date"))
    errs.append(_date(record.get("approved_date"), row, "approved_date"))
    return [e for e in errs if e]


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_VALIDATORS = {
    "patients":         validate_patient,
    "doctors":          validate_doctor,
    "staff_users":      validate_staff,
    "appointments":     validate_appointment,
    "prescriptions":    validate_prescription,
    "medical_records":  validate_medical_record,
    "clinic_info":      validate_clinic_info,
    "operating_hours":  validate_operating_hours,
    "insurance_claims": validate_insurance_claim,
}


def validate_row(entity_type: str, record: dict, row: int) -> list[RowError]:
    """
    Validate a single row for the given entity type.
    Returns a (possibly empty) list of RowError objects.
    """
    fn = _VALIDATORS.get(entity_type)
    if not fn:
        logger.warning(f"No validator found for entity_type='{entity_type}'")
        return []
    try:
        return fn(record, row)
    except Exception as e:
        logger.error(f"Validator error row {row}: {e}")
        return [RowError(row, "__validator__", f"Unexpected validation error: {e}")]
