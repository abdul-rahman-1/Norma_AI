from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
from app.logger import logger
import sys

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    if not settings.mongodb_uri:
        logger.error("CRITICAL ERROR: MONGODB_URI is not set in environment variables.")
        return

    try:
        db_instance.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_instance.db = db_instance.client[settings.mongodb_db_name]
        
        # Verify connection
        await db_instance.client.admin.command('ping')
        
        # Clean up existing problematic indexes if they exist
        try:
            # Dropping based on the error message index name
            await db_instance.db.patients.drop_index("phone_1")
            await db_instance.db.patients.drop_index("phone_number_1")
        except:
            pass 

        # Create Indexes for performance and uniqueness
        # We use partialFilterExpression to allow multiple 'null' values while enforcing uniqueness for strings
        await db_instance.db.patients.create_index(
            "phone_number", 
            unique=True, 
            partialFilterExpression={"phone_number": {"$type": "string"}}
        )
        await db_instance.db.appointments.create_index("patient_id")
        await db_instance.db.appointments.create_index("doctor_id")
        await db_instance.db.conversations.create_index([("phone", 1), ("timestamp", -1)])
        
        # Check collections
        collections = await db_instance.db.list_collection_names()
        logger.info(f"--- DATABASE CONNECTED ---")
        logger.info(f"DB Name: {settings.mongodb_db_name}")
        logger.info(f"Collections Found: {collections}")
        
    except Exception as e:
        logger.error(f"DATABASE CONNECTION ERROR: {e}")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

def get_db():
    return db_instance.db
