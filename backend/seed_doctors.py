import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid

async def seed_doctors():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.norma_ai
    
    doctors = [
        {
            "doctor_uuid": str(uuid.uuid4()),
            "full_name": "Dr. Sarah Ahmed",
            "specialty": "Cardiology",
            "license_number": "MD-88291",
            "whatsapp_number": "+1234567890",
            "email": "sarah.ahmed@normaclinic.com",
            "consultation_fee": 150.0,
            "bio": "Specialist in cardiovascular diseases with 10+ years of experience.",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "doctor_uuid": str(uuid.uuid4()),
            "full_name": "Dr. Michael Chen",
            "specialty": "Pediatrics",
            "license_number": "MD-99102",
            "whatsapp_number": "+1987654321",
            "email": "michael.chen@normaclinic.com",
            "consultation_fee": 120.0,
            "bio": "Compassionate pediatrician dedicated to child wellness and development.",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Clean existing doctors (optional, but good for clean seed)
    await db.doctors.delete_many({})
    
    result = await db.doctors.insert_many(doctors)
    print(f"Successfully seeded {len(result.inserted_ids)} doctors.")
    
    # Also ensure we have a user for one of them to test login if needed
    # (Assuming doctor role uses phone_number as login)
    await db.users.delete_many({"role": "doctor"})
    
    from bcrypt import hashpw, gensalt
    password_hash = hashpw("norma2026".encode('utf-8'), gensalt()).decode('utf-8')
    
    users = [
        {
            "phone_number": "1234567890",
            "name": "Dr. Sarah Ahmed",
            "email": "sarah.ahmed@normaclinic.com",
            "role": "doctor",
            "status": "active",
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    await db.users.insert_many(users)
    print("Seeded doctor user login: 1234567890 / norma2026")

if __name__ == "__main__":
    asyncio.run(seed_doctors())
