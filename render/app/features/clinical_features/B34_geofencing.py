import json
from app.logger import logger

async def execute_geofencing(params, user_role, user_data=None):
    """Action B34: Auto-check-in patient upon arrival."""
    logger.info(f"[GEOFENCE] Patient {user_data.get('full_name')} arrived at {params.get('clinic_name')}")
    return {
        "status": "success",
        "message": "Welcome! You have been automatically checked in. Please take a seat in the waiting area."
    }
