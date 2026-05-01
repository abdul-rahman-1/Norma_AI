from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_db
from app.config import get_settings
from app.api import auth, patients, uploads, dashboard, appointments, webhook, doctors, features, staff, bulk_upload, knowledge
from app.core.security import get_password_hash, decode_token
from datetime import datetime
from typing import Callable
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Permission & Audit Middleware
# ============================================================================

class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests for audit trail.
    Helps track user actions and detect unauthorized access attempts.
    """
    async def dispatch(self, request: Request, call_next: Callable):
        # Extract token if present
        auth_header = request.headers.get("authorization", "")
        user_info = None
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload:
                user_info = {
                    "username": payload.get("sub"),
                    "role": payload.get("role")
                }
        
        # Log request
        logger.info(f"API Request: {request.method} {request.url.path} - User: {user_info}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(f"API Response: {request.method} {request.url.path} - Status: {response.status_code}")
        
        # Store in audit_log collection for Admin view (Phase 8.3)
        try:
            db = get_db()
            if db is not None:
                audit_entry = {
                    "timestamp": datetime.utcnow(),
                    "method": request.method,
                    "path": request.url.path,
                    "user": user_info,
                    "status_code": response.status_code,
                    "ip_address": request.client.host if request.client else "unknown"
                }
                await db.audit_log.insert_one(audit_entry)
        except Exception as e:
            logger.error(f"Failed to write audit log to DB: {e}")
            
        return response

# Add audit middleware
app.add_middleware(AuditLogMiddleware)

app.include_router(auth.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(staff.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")
app.include_router(features.router, prefix="/api")
app.include_router(bulk_upload.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

async def seed_admin_user():
    db = get_db()
    admin_user = await db.login_details.find_one({"username": "norma_admin"})
    if not admin_user:
        admin_data = {
            "username": "norma_admin",
            "password_hash": get_password_hash("norma2026"),
            "name": "Norma Admin",
            "role": "admin",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await db.login_details.insert_one(admin_data)
        print("Default admin user 'norma_admin' created.")

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await seed_admin_user()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Norma AI API is running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
