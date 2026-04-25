from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash, decode_token
from app.db.mongodb import get_db
from app.schemas.models import User, UserCreate
from datetime import datetime, timedelta
from typing import Optional, List

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    phone_number: str = payload.get("sub")
    if phone_number is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Handle hardcoded admin
    if phone_number == "norma_admin":
        return {"phone_number": "norma_admin", "role": "admin", "name": "Norma Admin", "_id": "admin_id"}

    db = get_db()
    user = await db.users.find_one({"phone_number": phone_number})
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    user = await db.users.find_one({"phone_number": form_data.username})
    if not user or not verify_password(form_data.password, user.get("password_hash")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["phone_number"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

@router.post("/admin-login")
async def admin_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Hardcoded admin credentials as requested
    if form_data.username == "norma_admin" and form_data.password == "norma2026":
        access_token = create_access_token(
            data={"sub": "norma_admin", "role": "admin"}
        )
        return {"access_token": access_token, "token_type": "bearer", "role": "admin"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect admin username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

def check_role(allowed_roles: List[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        # Special case for hardcoded admin who might not be in the database
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

@router.post("/add-staff")
async def add_staff(
    user_in: UserCreate, 
    db=Depends(get_db), 
    current_user=Depends(check_role(["admin", "doctor"]))
):
    existing_user = await db.users.find_one({"phone_number": user_in.phone_number})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_dict = user_in.model_dump()
    if user_in.password:
        user_dict["password_hash"] = get_password_hash(user_in.password)
        del user_dict["password"]
    
    user_dict["role"] = "receptionist" # Staff maps to receptionist
    user_dict["created_at"] = user_dict["updated_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    return {"message": "Staff created successfully", "id": str(result.inserted_id)}

@router.post("/register")
async def register(user_in: UserCreate):
    db = get_db()
    existing_user = await db.users.find_one({"phone_number": user_in.phone_number})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user_dict = user_in.dict()
    if user_in.password:
        user_dict["password_hash"] = get_password_hash(user_in.password)
        del user_dict["password"]
    
    user_dict["created_at"] = user_dict["updated_at"] = datetime.utcnow()
    
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    return {"message": "User created successfully", "id": str(result.inserted_id)}
