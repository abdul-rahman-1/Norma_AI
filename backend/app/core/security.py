from datetime import datetime, timedelta
from typing import Optional, Any, List, Callable
from jose import jwt
import bcrypt
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import get_settings
from app.core.permissions import (
    UserRole, ResourceType, ActionType,
    check_resource_access, check_patient_not_user,
    get_role_from_token
)

settings = get_settings()

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError as e:
        return None


# ============================================================================
# Role-Based Access Control Functions
# ============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extract and validate the current user from JWT token.
    
    CRITICAL: Rejects any patient tokens.
    """
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # CRITICAL SECURITY CHECK: No patients allowed
    check_patient_not_user(payload)
    
    return payload


def require_role(*allowed_roles: str) -> Callable:
    """
    Decorator to enforce role-based access control.
    
    Usage:
        @require_role("admin", "doctor")
        async def my_endpoint(current_user = Depends(get_current_user)):
            ...
    
    Args:
        allowed_roles: Roles that are allowed to access this endpoint
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role", "").lower()
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role}' is not authorized. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


def require_permission(
    resource: ResourceType,
    action: ActionType
) -> Callable:
    """
    Decorator to enforce resource-based permissions.
    
    Usage:
        @require_permission(ResourceType.PATIENT, ActionType.CREATE)
        async def create_patient(current_user = Depends(get_current_user)):
            ...
    
    Args:
        resource: The resource type being accessed
        action: The action being performed
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = get_role_from_token(current_user)
        check_resource_access(user_role, resource, action, current_user)
        return current_user
    return permission_checker


def combine_permissions(*permissions: tuple) -> Callable:
    """
    Combine multiple permission checks.
    
    Usage:
        @combine_permissions(
            (ResourceType.PATIENT, ActionType.READ),
            (ResourceType.APPOINTMENT, ActionType.UPDATE)
        )
        async def my_endpoint(current_user = Depends(get_current_user)):
            ...
    """
    async def combined_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = get_role_from_token(current_user)
        for resource, action in permissions:
            check_resource_access(user_role, resource, action, current_user)
        return current_user
    return combined_checker


def get_user_role(current_user: dict) -> UserRole:
    """Extract and validate user role from token."""
    return get_role_from_token(current_user)





