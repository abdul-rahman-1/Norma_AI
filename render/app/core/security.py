from app.logger import logger

def enforce_role(user_role: str, allowed_roles: list, action_name: str = "Operation"):
    """
    STRICT RBAC ENFORCER:
    Validates if the user_role is within the allowed_roles list.
    """
    if not user_role:
        logger.error(f"[RBAC DENIED] {action_name}: No role identified.")
        return False, "Access denied. Identity not verified."

    if user_role.upper() == "ADMIN":
        # Admins can bypass most operational RBAC checks
        return True, None

    if user_role.upper() in [r.upper() for r in allowed_roles]:
        return True, None

    logger.warning(f"[RBAC DENIED] {action_name}: Role '{user_role}' not authorized. Allowed: {allowed_roles}")
    return False, f"Unauthorized. Only users with roles {allowed_roles} can perform this action."

# PERMISSION MAPS (Central Source of Truth)
RBAC_PERMISSIONS = {
    "MANAGE_PATIENTS": ["DOCTOR", "STAFF"],
    "MANAGE_STAFF": ["DOCTOR"],
    "MANAGE_DOCTORS": ["ADMIN"],
    "CLINIC_DATA_CRUD": ["DOCTOR", "ADMIN"],
    "APPOINTMENT_CRUD": ["PATIENT", "DOCTOR", "STAFF"], # Patients, Staff, and Doctors can now CRUD directly
    "VIEW_PHI": ["DOCTOR", "STAFF"] # Protected Health Info restricted to clinical staff
}
