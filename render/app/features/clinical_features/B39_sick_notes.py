import json

async def execute_sick_notes(params, user_role):
    """Action B39: Generate medical sick notes (PDF baseline)."""
    if user_role != "DOCTOR": return {"error": "Only doctors can issue sick notes."}
    
    return {
        "status": "success",
        "link": "https://portal.norma-ai.com/docs/sick-note-temp.pdf",
        "message": "Sick note generated and sent to patient."
    }
