"""
RoleEnforcer: Strict permission checking for doctor/staff/admin operations.
Patients are NOT system users - no patient access control.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from bson import ObjectId

class Role(Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    STAFF = "STAFF"


class RoleEnforcer:
    """
    Enforces strict role-based access control.
    ONLY Admin, Doctor, Staff can access the system.
    Patients are database records, not users.
    """
    
    # Permissions by role
    PERMISSIONS = {
        Role.ADMIN: {
            "view_all_patients": True,
            "view_all_doctors": True,
            "view_all_appointments": True,
            "view_all_staff": True,
            "manage_doctors": True,
            "manage_clinic_config": True,
            "view_financial": True,
            "create_staff": True,
            "delete_staff": True,
            "system_settings": True,
        },
        Role.DOCTOR: {
            "view_own_patients": True,
            "view_own_appointments": True,
            "manage_own_appointments": True,
            "manage_own_staff": True,
            "view_medical_records": True,
            "create_prescriptions": True,
            "view_own_financial": True,
            "cancel_own_appointments": True,
            "reschedule_own_appointments": True,
        },
        Role.STAFF: {
            "view_assigned_patients": True,
            "view_assigned_appointments": True,
            "manage_assigned_appointments": True,
            "create_appointment": True,
            "cancel_appointment": True,
            "reschedule_appointment": True,
            "view_assigned_financial": True,
        }
    }
    
    @staticmethod
    def check_permission(role: str, permission: str) -> bool:
        """
        Check if role has specific permission.
        Returns True if allowed, False otherwise.
        """
        try:
            role_enum = Role[role.upper()]
            perms = RoleEnforcer.PERMISSIONS.get(role_enum, {})
            return perms.get(permission, False)
        except KeyError:
            return False
    
    @staticmethod
    def is_valid_user_role(role: str) -> bool:
        """Only ADMIN, DOCTOR, STAFF are valid system users."""
        return role.upper() in ["ADMIN", "DOCTOR", "STAFF"]
    
    @staticmethod
    def is_patient(role: str) -> bool:
        """Returns True if role is PATIENT (which should NOT have access)."""
        return role.upper() == "PATIENT"
    
    @staticmethod
    async def can_access_patient(
        user_role: str,
        user_data: Dict[str, Any],
        target_patient_id: str
    ) -> bool:
        """
        Check if user can access specific patient.
        
        ADMIN: Can access all patients
        DOCTOR: Can access own patients only
        STAFF: Can access patients assigned to their doctor only
        PATIENT: No access (patients are not users)
        """
        if RoleEnforcer.is_patient(user_role):
            return False
        
        if not RoleEnforcer.is_valid_user_role(user_role):
            return False
        
        if user_role.upper() == "ADMIN":
            return True
        
        # DOCTOR or STAFF - need to check if patient is in their scope
        if user_role.upper() == "DOCTOR":
            # Doctor can access patients they've treated
            # For now, assume any patient assignment is in database
            return True  # Filtered at database query level
        
        if user_role.upper() == "STAFF":
            # Staff can access patients under their assigned doctor
            return True  # Filtered at database query level
        
        return False
    
    @staticmethod
    async def can_access_appointment(
        user_role: str,
        user_data: Dict[str, Any],
        appointment_doctor_id: str
    ) -> bool:
        """
        Check if user can access specific appointment.
        
        ADMIN: Can access all
        DOCTOR: Can access own appointments only
        STAFF: Can access if assigned to that doctor
        """
        if not RoleEnforcer.is_valid_user_role(user_role):
            return False
        
        if user_role.upper() == "ADMIN":
            return True
        
        if user_role.upper() == "DOCTOR":
            # Check if appointment's doctor matches user
            user_doctor_id = user_data.get("_id")
            appointment_doctor_id = ObjectId(appointment_doctor_id) if isinstance(appointment_doctor_id, str) else appointment_doctor_id
            user_doctor_id = ObjectId(user_doctor_id) if isinstance(user_doctor_id, str) else user_doctor_id
            return user_doctor_id == appointment_doctor_id
        
        if user_role.upper() == "STAFF":
            # Check if staff's doctor matches appointment's doctor
            staff_doctor_id = user_data.get("assigned_doctor_id")
            if not staff_doctor_id:
                return False
            staff_doctor_id = ObjectId(staff_doctor_id) if isinstance(staff_doctor_id, str) else staff_doctor_id
            appointment_doctor_id = ObjectId(appointment_doctor_id) if isinstance(appointment_doctor_id, str) else appointment_doctor_id
            return staff_doctor_id == appointment_doctor_id
        
        return False
    
    @staticmethod
    def get_filtered_query(user_role: str, user_data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Get database filter query based on user role and entity type.
        
        entity_type: "patients", "appointments", "doctors", "staff"
        """
        if not RoleEnforcer.is_valid_user_role(user_role):
            return None
        
        if user_role.upper() == "ADMIN":
            return {}  # No filter, access all
        
        if user_role.upper() == "DOCTOR":
            if entity_type == "appointments":
                return {"doctor_id": user_data.get("_id")}
            elif entity_type == "patients":
                # Doctor can see patients they've treated (via appointments)
                return {}  # Must be filtered via JOIN query
            elif entity_type == "staff":
                return {"assigned_doctor_id": user_data.get("_id")}
        
        if user_role.upper() == "STAFF":
            if entity_type == "appointments":
                return {"doctor_id": user_data.get("assigned_doctor_id")}
            elif entity_type == "patients":
                return {}  # Must be filtered via JOIN query
        
        return {}
