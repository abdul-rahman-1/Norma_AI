from app.core.security import RBAC_PERMISSIONS, enforce_role
from app.logger import logger

class ValidationService:
    @staticmethod
    def validate_rbac(user_role: str, permission_key: str, action_name: str = "Operation"):
        """
        Validates if the user has the required permission.
        """
        allowed_roles = RBAC_PERMISSIONS.get(permission_key, [])
        is_authorized, err_msg = enforce_role(user_role, allowed_roles, action_name)
        return is_authorized, err_msg

    @staticmethod
    def validate_required_fields(data: dict, required_fields: list):
        """
        Validates that all required fields are present in the data.
        """
        missing = [field for field in required_fields if field not in data or data[field] is None]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        return True, None

validation_service = ValidationService()
