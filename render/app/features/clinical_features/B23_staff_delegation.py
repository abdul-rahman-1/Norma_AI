from datetime import datetime
import uuid
from app.db.mongodb import get_profile_db
from app.services.whatsapp_service import whatsapp_service
from app.core.security import enforce_role
from app.logger import logger

async def execute(params, user_role, user_data=None, sender_phone=None):
    """
    Action B23: Staff Delegation
    Assign tasks to staff members.
    """
    allowed = ["DOCTOR", "ADMIN", "STAFF"]
    is_authorized, err_msg = enforce_role(user_role, allowed, action_name="B23_STAFF_DELEGATION")
    if not is_authorized:
        return {"status": "error", "message": err_msg}

    profile_db = get_profile_db()
    try:
        task_title = params.get("title")
        task_description = params.get("description")
        assigned_to_id = params.get("assigned_to_id") # staff_user_id
        priority = params.get("priority", "medium")

        if not all([task_title, assigned_to_id]):
            return {"status": "error", "message": "Task title and assignee are required."}

        staff_member = await profile_db.staff_users.find_one({"_id": assigned_to_id})
        if not staff_member:
            return {"status": "error", "message": "Assigned staff member not found."}

        task_data = {
            "task_uuid": str(uuid.uuid4()),
            "title": task_title,
            "description": task_description,
            "assigned_to": assigned_to_id,
            "assigned_by": user_data.get("_id") if user_data else "SYSTEM",
            "priority": priority,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Save task to a 'tasks' collection (assumed to exist or will be created on first write)
        await profile_db.tasks.insert_one(task_data)

        # Notify staff member
        if staff_member.get("phone_number"):
            msg = (
                f"📋 *New Task Assigned*\n"
                f"Title: {task_title}\n"
                f"Priority: {priority.upper()}\n"
                f"Assigned by: {user_data.get('full_name', 'Clinical Team')}\n"
                f"Please check your dashboard for details."
            )
            await whatsapp_service.send_custom_message(staff_member["phone_number"], msg)

        return {
            "status": "success", 
            "message": f"Task '{task_title}' assigned to {staff_member['full_name']}.",
            "task_id": task_data["task_uuid"]
        }

    except Exception as e:
        logger.error(f"B23_STAFF_DELEGATION_ERROR: {str(e)}")
        return {"status": "error", "message": f"Delegation failed: {str(e)}"}
