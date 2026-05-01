"""
column_mapper.py
----------------
AI-powered (Gemini Flash) mapping from arbitrary Excel column names
to canonical schema field names for each entity type.

The result is cached in the upload job so it is only called once per file.
"""

import json
import logging
from typing import Optional
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

# ---------------------------------------------------------------------------
# Schema definitions — what Gemini needs to know about each entity
# ---------------------------------------------------------------------------

ENTITY_SCHEMAS: dict[str, dict] = {
    "patients": {
        "required": ["full_name", "phone_number"],
        "optional": ["email", "date_of_birth", "gender", "address",
                     "medical_alerts", "insurance_provider", "insurance_id",
                     "notes", "preferred_language", "patient_uuid"]
    },
    "doctors": {
        "required": ["full_name", "whatsapp_number"],
        "optional": ["specialty", "license_number", "email", "phone",
                     "consultation_fee", "bio", "bio_ar", "full_name_ar",
                     "google_calendar_id", "doctor_uuid"]
    },
    "staff_users": {
        "required": ["full_name", "phone_number"],
        "optional": ["email", "role", "doctor_id", "notes"]
    },
    "appointments": {
        "required": ["patient_phone", "doctor_phone", "appointment_datetime"],
        "optional": ["reason", "status", "notes", "source"]
    },
    "prescriptions": {
        "required": ["patient_phone", "medication_name"],
        "optional": ["dosage", "frequency", "start_date", "end_date",
                     "prescribed_by", "notes"]
    },
    "medical_records": {
        "required": ["patient_phone", "record_type"],
        "optional": ["diagnosis", "symptoms", "treatment", "visit_date",
                     "doctor_phone", "notes"]
    },
    "clinic_info": {
        "required": ["key", "value"],
        "optional": ["language", "category", "notes"]
    },
    "operating_hours": {
        "required": ["day_of_week", "open_time", "close_time"],
        "optional": ["doctor_phone", "is_open", "break_start_time",
                     "break_end_time", "notes"]
    },
    "insurance_claims": {
        "required": ["patient_phone", "claim_number", "provider"],
        "optional": ["amount", "status", "submitted_date",
                     "approved_date", "notes"]
    },
}


# ---------------------------------------------------------------------------
# Fallback: simple heuristic mapping (no AI needed)
# ---------------------------------------------------------------------------

_COMMON_ALIASES: dict[str, list[str]] = {
    "full_name":            ["name", "full name", "patient name", "doctor name",
                             "staff name", "employee name", "fullname"],
    "phone_number":         ["phone", "mobile", "cell", "telephone", "tel",
                             "contact", "phone number", "mobile number"],
    "whatsapp_number":      ["whatsapp", "wa number", "whatsapp number", "wa"],
    "email":                ["email", "e-mail", "email address"],
    "date_of_birth":        ["dob", "birth date", "birthday", "date of birth"],
    "gender":               ["gender", "sex"],
    "address":              ["address", "location", "city"],
    "medical_alerts":       ["allergies", "alerts", "medical alerts", "conditions"],
    "notes":                ["notes", "remarks", "comments", "note"],
    "specialty":            ["specialty", "speciality", "department", "specialization"],
    "license_number":       ["license", "licence", "license no", "reg number"],
    "consultation_fee":     ["fee", "cost", "price", "consultation fee"],
    "appointment_datetime": ["appointment date", "appt date", "scheduled",
                             "date time", "appointment datetime", "scheduled_at"],
    "patient_phone":        ["patient phone", "patient mobile", "patient contact"],
    "doctor_phone":         ["doctor phone", "doctor mobile", "doctor contact"],
    "record_type":          ["record type", "type", "category"],
    "diagnosis":            ["diagnosis", "diagnose", "condition"],
    "symptoms":             ["symptoms", "complaints", "presenting"],
    "treatment":            ["treatment", "therapy", "procedure"],
    "visit_date":           ["visit date", "visit", "consultation date"],
    "medication_name":      ["medication", "medicine", "drug", "drug name"],
    "dosage":               ["dosage", "dose", "strength"],
    "frequency":            ["frequency", "times per day", "how often"],
    "claim_number":         ["claim number", "claim no", "claim id", "reference"],
    "provider":             ["provider", "insurance company", "insurer"],
    "day_of_week":          ["day", "day of week", "weekday"],
    "open_time":            ["open", "start", "start time", "opening time"],
    "close_time":           ["close", "end", "end time", "closing time"],
    "break_start_time":     ["break start", "lunch start"],
    "break_end_time":       ["break end", "lunch end"],
    "key":                  ["key", "setting", "field", "parameter"],
    "value":                ["value", "setting value", "content"],
}


def _heuristic_map(columns: list[str], entity_type: str) -> dict[str, Optional[str]]:
    """Fast fallback: map columns using alias tables."""
    schema = ENTITY_SCHEMAS.get(entity_type, {})
    all_fields = schema.get("required", []) + schema.get("optional", [])

    col_lower = {c.lower().strip(): c for c in columns}
    result: dict[str, Optional[str]] = {}

    for field in all_fields:
        result[field] = None
        # Direct match
        if field in col_lower:
            result[field] = col_lower[field]
            continue
        # Alias match
        for alias in _COMMON_ALIASES.get(field, []):
            if alias in col_lower:
                result[field] = col_lower[alias]
                break

    return result


# ---------------------------------------------------------------------------
# AI-powered mapper
# ---------------------------------------------------------------------------

async def map_columns(
    columns: list[str],
    sample_rows: list[dict],
    entity_type: str,
) -> dict[str, Optional[str]]:
    """
    Map Excel column names to canonical schema fields for the given entity type.

    Uses Gemini Flash with a structured prompt. Falls back to heuristic mapping
    if the AI response is unparseable.

    Returns:
        { "schema_field": "ExcelColumnName" | None }
    """
    schema = ENTITY_SCHEMAS.get(entity_type, {})
    all_fields = schema.get("required", []) + schema.get("optional", [])
    required_fields = schema.get("required", [])

    # Build a clean sample (max 3 rows, truncate values to 100 chars)
    clean_sample = []
    for row in sample_rows[:3]:
        clean_sample.append({
            k: str(v)[:100] if v is not None else None
            for k, v in row.items()
        })

    prompt = f"""
You are a data mapping assistant for a medical clinic management system.

TASK:
Map the Excel column names below to the canonical schema fields for the entity type "{entity_type}".

EXCEL COLUMNS:
{json.dumps(columns)}

SAMPLE DATA (first 3 rows):
{json.dumps(clean_sample, ensure_ascii=False, indent=2)}

CANONICAL SCHEMA FIELDS:
- Required: {json.dumps(required_fields)}
- Optional: {json.dumps(schema.get("optional", []))}

RULES:
1. Return ONLY a JSON object with schema field names as keys.
2. Values must be exact Excel column names from the list above, or null if no match.
3. Do NOT invent column names. Only use exact strings from the EXCEL COLUMNS list.
4. If multiple columns could match a field, choose the best one.
5. Required fields must be mapped if at all possible.

Return ONLY valid JSON, no explanation, no markdown.
Example: {{"full_name": "Patient Name", "phone_number": "Mobile", "email": null}}
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        mapping = json.loads(text)

        # Validate: only keep keys that are actual schema fields,
        # and only values that are actual column names or null
        col_set = set(columns)
        clean = {}
        for field in all_fields:
            val = mapping.get(field)
            if val and val in col_set:
                clean[field] = val
            else:
                clean[field] = None

        logger.info(f"AI column mapping for '{entity_type}': {clean}")
        return clean

    except Exception as e:
        logger.warning(f"AI column mapping failed ({e}), using heuristic fallback.")
        return _heuristic_map(columns, entity_type)
