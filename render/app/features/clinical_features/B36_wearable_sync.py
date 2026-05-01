import json
from app.db.mongodb import get_phi_db

async def execute_wearable_sync(params, user_role, user_data=None):
    """Action B36: Integrate Apple Health/Wearable data."""
    phi_db = get_phi_db()
    # Mock data integration
    health_data = params.get("health_metrics", {})
    await phi_db.medical_records.insert_one({
        "patient_id": user_data["_id"],
        "record_type": "WEARABLE_DATA",
        "content": json.dumps(health_data),
        "title": "Wearable Sync Update"
    })
    return {"status": "success", "message": "Health data synced."}
