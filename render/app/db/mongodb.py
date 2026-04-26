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
        # FORCE USE OF NORMA_AI
        db_instance.phi_db = db_instance.client["norma_ai"]
        db_instance.profile_db = db_instance.client["norma_ai"]
        
        await db_instance.client.admin.command('ping')
        
        # Ensure collections exist for the new schema
        logger.info(f"--- DATABASE CONNECTED (STRICT MODE) ---")
        logger.info(f"STRICT DB: norma_ai")
        
    except Exception as e:
        logger.error(f"DATABASE CONNECTION ERROR: {e}")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

def get_phi_db():
    return db_instance.phi_db

def get_profile_db():
    return db_instance.profile_db
