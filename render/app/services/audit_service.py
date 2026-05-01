from datetime import datetime
from app.db.mongodb import get_phi_db
from app.logger import logger

class AuditService:
    @staticmethod
    async def log_action(user_id: str, role: str, action: str, resource: str, details: dict, status: str = "success"):
        """
        Logs an action to the audit_log collection.
        """
        db = get_phi_db()
        log_entry = {
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "role": role,
            "action": action,
            "resource": resource,
            "details": details,
            "status": status
        }
        try:
            await db.audit_log.insert_one(log_entry)
        except Exception as e:
            logger.error(f"AUDIT_LOG_ERROR: {str(e)}")

audit_service = AuditService()
