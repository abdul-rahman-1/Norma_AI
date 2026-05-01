"""
type_detector.py
----------------
Detects the entity type from an Excel file's sheet names and column headers.
Uses rule-based heuristics — no AI call needed, fast and deterministic.

Supported entity types:
  patients, doctors, staff_users, appointments, prescriptions,
  medical_records, clinic_info, operating_hours, insurance_claims
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Known canonical aliases per entity type (lowercase)
# ---------------------------------------------------------------------------
SHEET_NAME_ALIASES: dict[str, list[str]] = {
    "patients":        ["patients", "patient", "clients", "client"],
    "doctors":         ["doctors", "doctor", "physicians", "physician"],
    "staff_users":     ["staff", "staff_users", "employees", "employee", "team"],
    "appointments":    ["appointments", "appointment", "appt", "appts", "bookings", "booking"],
    "prescriptions":   ["prescriptions", "prescription", "rx", "medications", "medication"],
    "medical_records": ["medical_records", "records", "medical", "history", "medrecords"],
    "clinic_info":     ["clinic_info", "clinic", "info", "settings", "configuration"],
    "operating_hours": ["operating_hours", "hours", "schedule", "working_hours"],
    "insurance_claims":["insurance_claims", "insurance", "claims", "claim"],
}

# Column header signatures — a set of columns whose presence strongly suggests an entity type
COLUMN_SIGNATURES: list[tuple[str, set[str]]] = [
    # Higher-specificity rules first
    ("doctors",          {"whatsapp_number", "license_number"}),
    ("doctors",          {"whatsapp_number", "specialty"}),
    ("staff_users",      {"doctor_id", "role"}),
    ("appointments",     {"appointment_datetime"}),
    ("appointments",     {"scheduled_at"}),
    ("prescriptions",    {"medication_name"}),
    ("prescriptions",    {"medication", "dosage"}),
    ("medical_records",  {"diagnosis", "symptoms"}),
    ("medical_records",  {"record_type", "visit_date"}),
    ("clinic_info",      {"key", "value", "category"}),
    ("operating_hours",  {"day_of_week", "open_time"}),
    ("operating_hours",  {"day_of_week", "close_time"}),
    ("insurance_claims", {"claim_number", "provider"}),
    ("insurance_claims", {"claim_number"}),
    # Lower-specificity — patient is the fallback
    ("patients",         {"patient_uuid"}),
    ("patients",         {"date_of_birth", "full_name"}),
    ("patients",         {"full_name", "phone_number"}),
    ("patients",         {"full_name", "phone"}),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_entity_type(
    columns: list[str],
    sheet_name: str = "",
    explicit_override: Optional[str] = None,
) -> str:
    """
    Detect the entity type for a given set of Excel column headers and sheet name.

    Args:
        columns:           List of column header strings from the Excel sheet.
        sheet_name:        Name of the Excel sheet (optional but improves accuracy).
        explicit_override: If the user explicitly specifies the entity type, use it directly.

    Returns:
        One of the 9 supported entity type strings.
    """
    # 0 — Hard override from caller
    if explicit_override:
        et = explicit_override.lower().strip()
        if et in SHEET_NAME_ALIASES:
            logger.info(f"Entity type override: {et}")
            return et
        logger.warning(f"Unknown explicit entity type '{et}', falling back to detection.")

    # 1 — Sheet name matching (fastest, most reliable when present)
    if sheet_name:
        sheet_lower = sheet_name.lower().strip()
        for entity_type, aliases in SHEET_NAME_ALIASES.items():
            if sheet_lower in aliases:
                logger.info(f"Entity type detected via sheet name '{sheet_name}': {entity_type}")
                return entity_type

    # 2 — Column signature matching
    normalised_cols = {c.lower().strip().replace(" ", "_") for c in columns if isinstance(c, str)}
    for entity_type, required_cols in COLUMN_SIGNATURES:
        if required_cols.issubset(normalised_cols):
            logger.info(f"Entity type detected via column signature {required_cols}: {entity_type}")
            return entity_type

    # 3 — Fallback: assume patients (most common upload)
    logger.warning(
        f"Could not confidently detect entity type from columns={list(normalised_cols)[:8]}, "
        f"sheet='{sheet_name}'. Defaulting to 'patients'."
    )
    return "patients"


def list_supported_entity_types() -> list[str]:
    """Return all supported entity type strings."""
    return list(SHEET_NAME_ALIASES.keys())
