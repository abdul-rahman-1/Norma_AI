from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
from app.logger import logger
import sys

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    phi_db = None
    profile_db = None

db_instance = MongoDB()

async def connect_to_mongo():
    if not settings.mongodb_uri:
        logger.error("CRITICAL ERROR: MONGODB_URI is not set.")
        return

    try:
        db_instance.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_instance.phi_db = db_instance.client[settings.mongodb_phi_db]
        db_instance.profile_db = db_instance.client[settings.mongodb_profile_db]
        
        # Verify connection
        await db_instance.client.admin.command('ping')
        
        # Create Indexes for PHI Database
        await db_instance.phi_db.patients.create_index("phone_number", unique=True)
        await db_instance.phi_db.appointments.create_index("patient_id")
        await db_instance.phi_db.patient_communications.create_index([("channel_identifier", 1), ("timestamp", -1)])
        
        # Create Indexes for Profile Database
        await db_instance.profile_db.doctors.create_index("whatsapp_number", unique=True)
        await db_instance.profile_db.staff_users.create_index("phone", unique=True)
        
        logger.info(f"--- DATABASE CONNECTED ---")
        logger.info(f"PHI DB: {settings.mongodb_phi_db}")
        logger.info(f"Profile DB: {settings.mongodb_profile_db}")
        
    except Exception as e:
        logger.error(f"DATABASE CONNECTION ERROR: {e}")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

def get_phi_db():
    return db_instance.phi_db

def get_profile_db():
    return db_instance.profile_db
