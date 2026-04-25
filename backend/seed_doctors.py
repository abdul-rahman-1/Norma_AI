import asyncio
import os
import sys
from datetime import datetime
import uuid

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.mongodb import connect_to_mongo, get_db
from app.core.security import get_password_hash

async def seed_data():
    await connect_to_mongo()
    db = get_db()
    
    # 1. Seed Admin
    admin_check = await db.login_details.find_one({"username": "norma_admin"})
    if not admin_check:
        admin_user = {
            "username": "norma_admin",
            "password_hash": get_password_hash("norma2026"),
            "role": "admin",
            "name": "System Admin",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.login_details.insert_one(admin_user)
        print("Admin user 'norma_admin' seeded.")
    else:
        print("Admin user already exists.")

    # 2. Seed 2 Doctors
    doctors_data = [
        {
            "doctor_uuid": str(uuid.uuid4()),
            "full_name": "Dr. Sarah Ahmed",
            "specialty": "Cardiology",
            "whatsapp_number": "9876543210",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "doctor_uuid": str(uuid.uuid4()),
            "full_name": "Dr. Omar Khan",
            "specialty": "Pediatrics",
            "whatsapp_number": "9876543211",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]

    for doc in doctors_data:
        check = await db.doctors.find_one({"whatsapp_number": doc["whatsapp_number"]})
        if not check:
            # Insert into doctors collection
            await db.doctors.insert_one(doc)
            
            # Create login for doctor
            doctor_login = {
                "phone_number": doc["whatsapp_number"],
                "password_hash": get_password_hash("norma2026"),
                "role": "doctor",
                "name": doc["full_name"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.login_details.insert_one(doctor_login)
            print(f"Doctor {doc['full_name']} seeded.")
        else:
            print(f"Doctor {doc['full_name']} already exists.")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
