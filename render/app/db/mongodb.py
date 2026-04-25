from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import sys

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_instance = MongoDB()

async def connect_to_mongo():
    if not settings.mongodb_uri:
        print("CRITICAL ERROR: MONGODB_URI is not set in environment variables.")
        sys.stdout.flush()
        return

    try:
        db_instance.client = AsyncIOMotorClient(settings.mongodb_uri)
        db_instance.db = db_instance.client[settings.mongodb_db_name]
        
        # Verify connection
        await db_instance.client.admin.command('ping')
        
        # Clean up existing problematic indexes if they exist
        try:
            await db_instance.db.patients.drop_index("phone_number")
            await db_instance.db.patients.drop_index("phone_number_1")
        except:
            pass # Ignore if indexes don't exist

        # Create Indexes for performance and uniqueness
        # partialFilterExpression ensures that uniqueness is only enforced for documents where the field is a string (ignoring nulls)
        await db_instance.db.patients.create_index(
            "phone", 
            unique=True, 
            partialFilterExpression={"phone": {"$type": "string"}}
        )
        await db_instance.db.patients.create_index(
            "phone_number", 
            partialFilterExpression={"phone_number": {"$type": "string"}}
        )
        await db_instance.db.appointments.create_index("patient_id")
        await db_instance.db.appointments.create_index("doctor_id")
        await db_instance.db.conversations.create_index([("phone", 1), ("timestamp", -1)])
        
        # Check collections
        collections = await db_instance.db.list_collection_names()
        print(f"--- DATABASE CONNECTED ---")
        print(f"DB Name: {settings.mongodb_db_name}")
        print(f"Collections Found: {collections}")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"DATABASE CONNECTION ERROR: {e}")
        sys.stdout.flush()
        # In a real production app, we might want to exit if DB is unreachable
        # os._exit(1) 

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

def get_db():
    return db_instance.db
