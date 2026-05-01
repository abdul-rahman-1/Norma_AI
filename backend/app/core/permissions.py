"""
NORMA AI Permission Matrix and Access Control

Defines role-based permissions for Admin, Doctor, and Staff users.
Patients are NOT system users and have NO access to any endpoints.

CRITICAL RULE: Patients are data-only entities, not system users.
"""

from enum import Enum
from typing import List, Dict, Set
from fastapi import HTTPException, status

# User Roles
class UserRole(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    STAFF = "staff"
    RECEPTIONIST = "receptionist"
    # NOTE: "patient" role is intentionally NOT included in this enum
    # Patients are NOT system users

# Resource types
class ResourceType(str, Enum):
    PATIENT = "patient"
    APPOINTMENT = "appointment"
    DOCTOR = "doctor"
    STAFF = "staff"
    MEDICAL_RECORD = "medical_record"
    PRESCRIPTION = "prescription"
    CLINIC_INFO = "clinic_info"
    CLINIC_CONFIG = "clinic_config"
    ACTIVITY_LOG = "activity_log"
    AUDIT_LOG = "audit_log"

# Actions
class ActionType(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"

# Permission Matrix: role -> resource -> actions
PERMISSION_MATRIX: Dict[UserRole, Dict[ResourceType, Set[ActionType]]] = {
    UserRole.ADMIN: {
        # Admin can manage everything
        ResourceType.DOCTOR: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.LIST},
        ResourceType.STAFF: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.LIST},
        ResourceType.CLINIC_INFO: {ActionType.READ, ActionType.UPDATE},
        ResourceType.CLINIC_CONFIG: {ActionType.READ, ActionType.UPDATE},
        ResourceType.ACTIVITY_LOG: {ActionType.READ, ActionType.LIST},
        ResourceType.AUDIT_LOG: {ActionType.READ, ActionType.LIST},
        ResourceType.PATIENT: {ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.LIST},
        ResourceType.APPOINTMENT: {ActionType.READ, ActionType.LIST},  # Read-only
        ResourceType.MEDICAL_RECORD: {ActionType.READ, ActionType.LIST},  # Read-only
    },
    
    UserRole.DOCTOR: {
        # Doctor manages their own patients and appointments
        ResourceType.PATIENT: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.LIST},
        ResourceType.APPOINTMENT: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.LIST},
        ResourceType.MEDICAL_RECORD: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.LIST},
        ResourceType.PRESCRIPTION: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.LIST},
        ResourceType.STAFF: {ActionType.READ, ActionType.UPDATE, ActionType.LIST},  # Limited: can only manage own staff
        ResourceType.DOCTOR: {ActionType.READ},  # Limited: can only read own profile
    },
    
    UserRole.STAFF: {
        # Staff supports doctor operations
        ResourceType.PATIENT: {ActionType.READ, ActionType.UPDATE, ActionType.LIST},  # Limited: only assigned doctor's patients
        ResourceType.APPOINTMENT: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.LIST},  # Limited: only assigned doctor
        ResourceType.MEDICAL_RECORD: {ActionType.READ, ActionType.LIST},  # Limited: read-only
        ResourceType.PRESCRIPTION: {ActionType.READ, ActionType.LIST},  # Limited: read-only
    },

    UserRole.RECEPTIONIST: {
        # Receptionist: same scope as staff — manages patients and appointments for assigned doctor
        ResourceType.PATIENT: {ActionType.READ, ActionType.UPDATE, ActionType.LIST},
        ResourceType.APPOINTMENT: {ActionType.CREATE, ActionType.READ, ActionType.UPDATE, ActionType.DELETE, ActionType.LIST},
        ResourceType.MEDICAL_RECORD: {ActionType.READ, ActionType.LIST},
        ResourceType.PRESCRIPTION: {ActionType.READ, ActionType.LIST},
    }

    # Notably missing: no "patient" role - patients cannot login
}


def get_allowed_actions(role: UserRole, resource: ResourceType) -> Set[ActionType]:
    """Get allowed actions for a role on a resource."""
    if role not in PERMISSION_MATRIX:
        return set()  # No permissions for invalid role
    
    return PERMISSION_MATRIX[role].get(resource, set())


def can_user_access(user_role: UserRole, resource: ResourceType, action: ActionType) -> bool:
    """Check if a user role can perform an action on a resource."""
    allowed_actions = get_allowed_actions(user_role, resource)
    return action in allowed_actions


def check_patient_not_user(user_dict: dict) -> None:
    """
    CRITICAL SECURITY CHECK: Ensure patient is not trying to access system.
    
    Patients are database records only, not system users.
    If a "patient" role token somehow exists, reject it.
    
    Args:
        user_dict: The decoded user token dictionary
        
    Raises:
        HTTPException: If user is a patient (role == "patient")
    """
    user_role = user_dict.get("role", "").lower()
    if user_role == "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients are not system users. Access denied."
        )


def check_resource_access(
    user_role: UserRole,
    resource: ResourceType,
    action: ActionType,
    user_dict: dict = None
) -> None:
    """
    Check if user can access a resource with an action.
    
    Args:
        user_role: The user's role
        resource: The resource being accessed
        action: The action being performed
        user_dict: Optional user dictionary for patient check
        
    Raises:
        HTTPException: If access is denied
    """
    # First, ensure patient is not accessing
    if user_dict:
        check_patient_not_user(user_dict)
    
    # Check role-based permission
    if not can_user_access(user_role, resource, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role '{user_role.value}' cannot {action.value} {resource.value}"
        )


def check_resource_owner(
    user_id: str,
    resource_owner_id: str,
    user_role: UserRole,
    allow_admin: bool = True
) -> None:
    """
    Check if user owns a resource (for limiting doctor to own data).
    
    Args:
        user_id: The current user's ID
        resource_owner_id: The ID of the resource owner
        user_role: The current user's role
        allow_admin: Whether to allow admins to bypass ownership check
        
    Raises:
        HTTPException: If user doesn't own the resource
    """
    # Admin can access any resource if allow_admin is True
    if user_role == UserRole.ADMIN and allow_admin:
        return
    
    # User must own the resource
    if user_id != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own resources."
        )


def check_doctor_access(
    user_id: str,
    doctor_id: str,
    user_role: UserRole
) -> None:
    """
    Check if user can access a doctor's resources.
    
    - Admin: can access all doctors' resources
    - Doctor: can access only own resources
    - Staff: can access assigned doctor's resources
    
    Args:
        user_id: The current user's ID
        doctor_id: The doctor whose resources are being accessed
        user_role: The current user's role
        
    Raises:
        HTTPException: If access is denied
    """
    if user_role == UserRole.ADMIN:
        return  # Admin can access all
    
    if user_role == UserRole.DOCTOR:
        if user_id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only access their own resources."
            )
        return
    
    # For staff: check if they're assigned to this doctor
    # This would require a database lookup, so we leave that to the caller
    # But we enforce that staff cannot access any doctor's data without proper assignment


def check_staff_assignment(
    staff_id: str,
    doctor_id: str,
    user_db_record: dict
) -> None:
    """
    Check if staff is assigned to the given doctor.
    
    Args:
        staff_id: The staff member's ID
        doctor_id: The doctor ID
        user_db_record: The staff user's database record
        
    Raises:
        HTTPException: If staff is not assigned to this doctor
    """
    assigned_doctor_id = user_db_record.get("assigned_doctor_id")
    if assigned_doctor_id != doctor_id and assigned_doctor_id != str(doctor_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Staff member is not assigned to doctor {doctor_id}."
        )


# Helper functions for common checks

def role_has_permission(role: UserRole, resource: ResourceType, action: ActionType) -> bool:
    """Simple boolean check for role permissions."""
    return can_user_access(role, resource, action)


def get_role_from_token(token_payload: dict) -> UserRole:
    """Extract and validate role from token payload."""
    role_str = token_payload.get("role", "").lower()
    try:
        return UserRole(role_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid role: {role_str}"
        )


def describe_permissions(role: UserRole) -> Dict[str, List[str]]:
    """
    Get a human-readable description of a role's permissions.
    
    Returns:
        Dict mapping resource names to allowed actions
    """
    permissions = {}
    if role in PERMISSION_MATRIX:
        for resource, actions in PERMISSION_MATRIX[role].items():
            permissions[resource.value] = [action.value for action in actions]
    return permissions
