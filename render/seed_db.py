import asyncio
import uuid
import json
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "norma_ai"

async def seed_data():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Clean up existing data for a fresh start
    collections = [
        "clinic_info", "doctors", "patients", "appointments", 
        "medical_records", "prescriptions", "staff_users", 
        "insurance_claims", "conversations"
    ]
    for coll in collections:
        await db[coll].delete_many({})
        
    print(f"🌱 Seeding database: {DB_NAME}...")

    # 1. Clinic Info
    await db.clinic_info.insert_one({
        "clinic_uuid": str(uuid.uuid4()),
        "clinic_name": "Norma Global Health Center",
        "phone": "+10000000000",
        "whatsapp_number": "+10000000000",
        "address": "77 Medical Plaza, Tech City",
        "timezone": "UTC",
        "subscription_plan": "Enterprise"
    })

    # 2. Doctors
    doctor_ids = [ObjectId() for _ in range(3)]
    specialties = ["Cardiology", "Dermatology", "General Practice"]
    doctor_names = ["Dr. Sarah Smith", "Dr. James Wilson", "Dr. Elena Rodriguez"]
    
    for i in range(3):
        await db.doctors.insert_one({
            "_id": doctor_ids[i],
            "doctor_uuid": str(uuid.uuid4()),
            "full_name": doctor_names[i],
            "specialty": specialties[i],
            "whatsapp_number": f"+1999000000{i+1}",
            "consultation_fee": 150.0 + (i * 50),
            "is_active": True
        })

    # 3. Staff & Admins
    roles = ["ADMIN", "STAFF", "STAFF"]
    staff_names = ["Chief Admin", "Nurse Joy", "Receptionist Sam"]
    for i in range(3):
        await db.staff_users.insert_one({
            "user_uuid": str(uuid.uuid4()),
            "full_name": staff_names[i],
            "email": f"staff{i}@norma.ai",
            "phone": f"+1888000000{i+1}",
            "role": roles[i]
        })

    # 4. Patients
    patient_ids = [ObjectId() for _ in range(5)]
    patient_names = ["Alice Johnson", "Bob Miller", "Charlie Davis", "Diana Prince", "Edward Norton"]
    for i in range(5):
        await db.patients.insert_one({
            "_id": patient_ids[i],
            "patient_uuid": str(uuid.uuid4()),
            "full_name": patient_names[i],
            "phone_number": f"+1777000000{i+1}",
            "email": f"patient{i}@example.com",
            "date_of_birth": "1980-01-01",
            "medical_alerts": "None" if i % 2 == 0 else "High Blood Pressure",
            "insurance_provider": "HealthShield" if i < 3 else "GlobalCare",
            "is_active": True,
            "created_at": datetime.utcnow()
        })

    # 5. Appointments (Trigger automation tests)
    now = datetime.utcnow()
    
    # Appointment in 1 hour (Test Proactive Alerts)
    one_hour_later = (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    await db.appointments.insert_one({
        "appointment_uuid": str(uuid.uuid4()),
        "patient_id": patient_ids[0],
        "doctor_id": doctor_ids[0],
        "appointment_datetime": one_hour_later,
        "status": "scheduled",
        "appointment_type": "Follow-up",
        "chief_complaint": "Post-surgery check",
        "reminder_sent": False
    })

    # Appointments for Today's Briefing (Test Daily Briefing)
    today_str = now.strftime("%Y-%m-%d")
    for i in range(1, 4):
        await db.appointments.insert_one({
            "appointment_uuid": str(uuid.uuid4()),
            "patient_id": patient_ids[i],
            "doctor_id": doctor_ids[0], # Multiple for Dr. Smith
            "appointment_datetime": f"{today_str} 1{i}:00",
            "status": "scheduled",
            "appointment_type": "Consultation"
        })

    # 6. Medical Records & Prescriptions
    await db.medical_records.insert_one({
        "record_uuid": str(uuid.uuid4()),
        "patient_id": patient_ids[0],
        "record_type": "Clinical Note",
        "title": "Initial Assessment",
        "content": "Patient reports mild fatigue. BP slightly elevated.",
        "doctor_id": doctor_ids[0]
    })

    await db.prescriptions.insert_one({
        "prescription_uuid": str(uuid.uuid4()),
        "patient_id": patient_ids[0],
        "medications": [{"name": "Lisinopril", "dosage": "10mg", "frequency": "Daily"}],
        "filled_status": "active"
    })

    # 7. Insurance Claims
    await db.insurance_claims.insert_one({
        "claim_uuid": str(uuid.uuid4()),
        "patient_id": patient_ids[0],
        "amount": 250.0,
        "status": "processed",
        "provider": "HealthShield"
    })

    print("✅ Bulk mock data seeded successfully!")
    print(f"   - Doctors: {len(doctor_names)}")
    print(f"   - Patients: {len(patient_names)}")
    print(f"   - Appointments: 4 (including one-hour alert trigger)")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_data())
