"""
SessionContext: Tracks conversation state for Doctor/Staff/Admin ONLY.
Patients are NOT system users - no patient sessions.
"""

from typing import Optional, Dict
import threading
from app.core.role_enforcer import Role, RoleEnforcer

class SessionContext:
    """
    Per-user session tracking for Admin/Doctor/Staff.
    IMPORTANT: Patients are NOT users, so they have NO sessions.
    """
    _contexts: Dict[str, 'SessionContext'] = {}
    _lock = threading.Lock()

    def __init__(self, user_id: str, user_phone: str):
        self.user_id = user_id
        self.user_phone = user_phone
        
        # User identity (only for admin/doctor/staff)
        self.user_role: Optional[str] = None  # ADMIN, DOCTOR, STAFF
        self.full_name: Optional[str] = None
        
        # Context for operations
        self.current_doctor: Optional[str] = None  # Doctor being managed/referenced
        self.current_appointment: Optional[str] = None
        self.current_patient: Optional[str] = None  # Patient being managed (not a user)
        self.current_operation: Optional[str] = None
        self.last_message: Optional[str] = None
        
        # Permissions
        self.permissions: Dict[str, bool] = {}

    @classmethod
    def get(cls, user_phone: str, user_id: str = None) -> 'SessionContext':
        """Get or create session (only for valid users, not patients)."""
        with cls._lock:
            key = user_phone
            if key not in cls._contexts:
                cls._contexts[key] = SessionContext(user_id or key, user_phone)
            return cls._contexts[key]
    
    @classmethod
    def get_by_phone(cls, phone: str) -> Optional['SessionContext']:
        """Get existing session by phone."""
        with cls._lock:
            return cls._contexts.get(phone)

    def set_user(self, role: str, user_data: Dict, doctor_name: Optional[str] = None):
        """Set user identity. Only valid for ADMIN, DOCTOR, STAFF."""
        if not RoleEnforcer.is_valid_user_role(role):
            raise ValueError(f"Invalid user role: {role}")
        
        self.user_role = role.upper()
        self.user_id = str(user_data.get("_id", self.user_id))
        self.full_name = user_data.get("full_name", "Unknown")
        
        # For staff: store assigned doctor
        if role.upper() == "STAFF" and "assigned_doctor_id" in user_data:
            self.current_doctor = str(user_data["assigned_doctor_id"])
        
        # Load permissions for this role
        self._load_permissions()
    
    def _load_permissions(self):
        """Load role-based permissions."""
        if not self.user_role:
            return
        
        for perm_name in RoleEnforcer.PERMISSIONS.get(Role[self.user_role], {}).keys():
            self.permissions[perm_name] = RoleEnforcer.check_permission(self.user_role, perm_name)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission."""
        return self.permissions.get(permission, False)

    def update(self, doctor=None, appointment=None, patient=None, operation=None, last_message=None):
        """Update context for current operation."""
        if doctor is not None:
            self.current_doctor = doctor
        if appointment is not None:
            self.current_appointment = appointment
        if patient is not None:
            self.current_patient = patient  # Patient being managed, not a user
        if operation is not None:
            self.current_operation = operation
        if last_message is not None:
            self.last_message = last_message

    def clear(self):
        """Clear operation context (keep user identity)."""
        self.current_doctor = None
        self.current_appointment = None
        self.current_patient = None
        self.current_operation = None
        self.last_message = None
    
    def get_context_dict(self) -> Dict:
        """Return context as dictionary for AI."""
        return {
            "user_role": self.user_role,
            "user_name": self.full_name,
            "current_doctor": self.current_doctor,
            "current_appointment": self.current_appointment,
            "current_patient": self.current_patient,
            "current_operation": self.current_operation,
            "permissions": list(self.permissions.keys()),
        }

