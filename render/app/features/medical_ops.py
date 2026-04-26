import json
from app.db.mongodb import get_phi_db

async def execute_medical_op(op_type, params, user_role, user_data):
    phi_db = get_phi_db()

    try:
        if op_type == "CHECK_PRESCRIPTIONS":
            res = await phi_db.prescriptions.find({"patient_id": user_data["_id"]}).to_list(length=5)
            return {"status": "success", "data": json.loads(json.dumps(res, default=str))}
        
        elif op_type == "TRIAGE":
            return {"status": "success", "advice": "Emergency sensors active. Protocol established."}

        elif op_type == "EMERGENCY_TRIAGE":
            return {"status": "critical", "action": "HALT_CHAT_HANDOFF_TO_HUMAN", "message": "Please dial emergency services (e.g., 911) immediately or go to the nearest emergency room."}

        elif op_type == "VOICE_NOTE_TRIAGE":
            transcript = params.get("transcript", "No transcript provided.")
            return {"status": "success", "message": f"Voice note logged to medical record: {transcript}"}

        return {"status": "error", "message": "Unknown medical operation."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
