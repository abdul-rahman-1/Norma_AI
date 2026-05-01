import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Mock settings or import them
sys.path.append(os.getcwd())
from app.config import get_settings
settings = get_settings()

async def check():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]
    print(f"Connecting to {settings.mongodb_db_name}...")
    
    # Check admin
    admin = await db.login_details.find_one({"role": "admin"})
    print(f"Admin user in login_details: {admin is not None}")
    if admin:
        print(f"Admin details: { {k: v for k, v in admin.items() if k != 'password_hash'} }")
    
    # Check all users in login_details
    users = await db.login_details.find().to_list(length=10)
    print(f"Total users in login_details: {len(users)}")
    for u in users:
        print(f" - {u.get('username')} ({u.get('role')})")

if __name__ == "__main__":
    asyncio.run(check())
