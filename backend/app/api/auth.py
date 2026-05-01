from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    create_access_token, verify_password, get_password_hash,
    decode_token, get_current_user, require_role
)
from app.core.permissions import check_patient_not_user
from app.db.mongodb import get_db
from app.schemas.models import User, UserCreate, OTPLogin
from datetime import datetime, timedelta
from typing import Optional, List
import random
from pydantic import BaseModel
import httpx
import re
from app.config import get_settings

settings = get_settings()

def normalize_phone(phone: str) -> str:
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    if not clean_phone.startswith('+'):
        # Just prepend + if missing, assuming country code is included. 
        # If length is 10, it might be an Indian number missing +91 or US missing +1.
        # We will just prepend + for now to match +1234567890 test case if user typed 1234567890
        clean_phone = f"+{clean_phone}"
    return clean_phone


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/admin-login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Admin login with static credentials.
    Username: norma_admin
    Password: norma2026
    """
    db = get_db()
    admin = await db.login_details.find_one({
        "username": form_data.username,
        "role": "admin"
    })

    if not admin or not verify_password(form_data.password, admin.get("password_hash")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": admin["username"],
            "role": "admin",
            "_id": str(admin["_id"]),
            "assigned_doctor_id": None
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "admin",
        "name": admin.get("name", "System Admin")
    }

class OTPRequest(BaseModel):
    phone_number: str

@router.post("/request-otp")
async def request_otp(otp_request: OTPRequest, db=Depends(get_db)):
    """
    Request an OTP for doctor/staff login.
    
    CRITICAL: Patients are NOT allowed to request OTP.
    Only doctor, staff, receptionist roles can login.
    """
    normalized_phone = normalize_phone(otp_request.phone_number)
    
    # Try exact match first, then normalized
    login_info = await db.login_details.find_one({"phone_number": otp_request.phone_number})
    if not login_info:
        login_info = await db.login_details.find_one({"phone_number": normalized_phone})
        
    if not login_info:
        raise HTTPException(status_code=400, detail="Phone number not registered.")

    user_role = login_info.get("role", "").lower()
    
    # CRITICAL SECURITY CHECK: Reject patient role
    if user_role == "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients cannot login to this system."
        )
    
    # Only allow doctor, staff, receptionist
    if user_role not in ["doctor", "receptionist", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="OTP login not available for this user role."
        )

    otp = str(random.randint(100000, 999999))
    otp_expires_at = datetime.utcnow() + timedelta(minutes=5)

    await db.login_details.update_one(
        {"_id": login_info["_id"]},
        {"$set": {"otp": otp, "otp_expires_at": otp_expires_at}}
    )

    message_body = f"Your Norma AI login code is: {otp}. It is valid for 5 minutes."
    
    # Send via Render service instead of local Twilio client
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.render_service_url}/api/send-message",
                json={"phone_number": otp_request.phone_number, "message": message_body},
                timeout=10.0
            )
    except Exception as e:
        print(f"Failed to send OTP via render service: {e}")

    return {"message": "OTP sent successfully."}


@router.post("/login")
async def login_with_otp(form_data: OTPLogin, db=Depends(get_db)):
    """
    Login with phone number and OTP.
    
    CRITICAL: Patients are NOT allowed to login.
    """
    normalized_phone = normalize_phone(form_data.phone_number)
    
    # Try exact match first, then normalized
    login_info = await db.login_details.find_one({"phone_number": form_data.phone_number})
    if not login_info:
        login_info = await db.login_details.find_one({"phone_number": normalized_phone})

    if not login_info:
        raise HTTPException(status_code=404, detail="User not found.")

    user_role = login_info.get("role", "").lower()
    
    # CRITICAL SECURITY CHECK: Reject patient role
    if user_role == "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients cannot login to this system."
        )

    if not login_info.get("otp") or login_info.get("otp") != form_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP.")

    if datetime.utcnow() > login_info.get("otp_expires_at", datetime.utcnow() + timedelta(days=1)):
        # Invalidate OTP after check
        await db.login_details.update_one(
            {"_id": login_info["_id"]},
            {"$unset": {"otp": "", "otp_expires_at": ""}}
        )
        raise HTTPException(status_code=400, detail="OTP has expired.")

    # Clear OTP after successful login
    await db.login_details.update_one(
        {"_id": login_info["_id"]},
        {"$unset": {"otp": "", "otp_expires_at": ""}}
    )

    access_token = create_access_token(
        data={
            "sub": login_info["username"],
            "role": login_info["role"],
            "_id": str(login_info["_id"]),
            "assigned_doctor_id": str(login_info["assigned_doctor_id"]) if login_info.get("assigned_doctor_id") else None
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": login_info.get("role"),
        "name": login_info.get("name")
    }

@router.post("/add-staff")
async def add_staff(
    user_in: UserCreate,
    db=Depends(get_db),
    current_user=Depends(require_role("admin", "doctor"))
):
    """
    Add a new staff member.
    Only admin and doctor can add staff.
    """
    # Check login_details
    existing_login = await db.login_details.find_one({
        "$or": [
            {"phone_number": user_in.phone_number},
            {"username": user_in.email}
        ]
    })
    if existing_login:
        raise HTTPException(status_code=400, detail="User already exists")

    password_hash = get_password_hash(user_in.password) if user_in.password else None

    # Write to login_details for authentication and profile
    login_entry = {
        "identifier": user_in.phone_number,
        "phone_number": user_in.phone_number,
        "username": user_in.email,
        "name": user_in.name,
        "password_hash": password_hash,
        "role": "staff",
        "assigned_doctor_id": current_user.get("_id"),  # Link to assigning doctor
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db.login_details.insert_one(login_entry)
    return {"message": "Staff created successfully", "id": str(result.inserted_id)}

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update user profile.
    Accessible to all authenticated users (non-patients).
    """
    update_fields = {"updated_at": datetime.utcnow()}
    
    if profile_data.name:
        update_fields["name"] = profile_data.name
        
    if profile_data.password:
        update_fields["password_hash"] = get_password_hash(profile_data.password)
        
    if not update_fields:
        return {"message": "No fields to update"}
        
    await db.login_details.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_fields}
    )
    
    return {"message": "Profile updated successfully", "name": update_fields.get("name", current_user.get("name"))}

