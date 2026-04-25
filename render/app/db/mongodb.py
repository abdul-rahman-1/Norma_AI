from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import sys

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    try:
        db_instance.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_instance.db = db_instance.client[settings.mongodb_db_name]
        
        # Verify connection
        await db_instance.client.admin.command('ping')
        
        # Check collections
        collections = await db_instance.db.list_collection_names()
        print(f"--- DATABASE CONNECTED ---")
        print(f"DB Name: {settings.mongodb_db_name}")
        print(f"Collections Found: {collections}")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"DATABASE CONNECTION ERROR: {e}")
        sys.stdout.flush()

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

def get_db():
    return db_instance.db
