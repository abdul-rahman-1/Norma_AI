from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import PyObjectId

class StaffBase(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    doctor_id: Optional[PyObjectId] = None
    is_active: bool = True

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    doctor_id: Optional[PyObjectId] = None
    is_active: Optional[bool] = None

class Staff(StaffBase):
    id: PyObjectId

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = { "ObjectId": str }
