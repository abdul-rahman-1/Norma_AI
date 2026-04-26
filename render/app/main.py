from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api import webhook
from app.logger import logger
from app.services.automation_service import automation_service
import asyncio
from datetime import datetime

app = FastAPI(title="Norma AI Standalone Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This makes the webhook live at exactly /webhook
app.include_router(webhook.router)

async def automation_loop():
    """Infinite loop for background tasks."""
    while True:
        try:
            # Check for 1-hour alerts every minute
            await automation_service.run_upcoming_alerts()
            
            # Briefings logic: run if it's 8:00 AM UTC and hasn't run yet
            now = datetime.utcnow()
            if now.hour == 8 and now.minute == 0:
                await automation_service.send_doctor_daily_briefing()
                
            await asyncio.sleep(60) # Run every minute
        except Exception as e:
            logger.error(f"AUTOMATION_LOOP ERROR: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup():
    await connect_to_mongo()
    # Start the automation loop in the background
    asyncio.create_task(automation_loop())

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()

@app.get("/")
async def health():
    return {"status": "operational"}
