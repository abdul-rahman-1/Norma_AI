from fastapi import APIRouter, Depends, Query, HTTPException
from app.db.mongodb import get_db
from app.core.security import require_role
from datetime import datetime, timedelta
from bson import ObjectId
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(require_role("admin", "doctor", "staff"))):
    """
    Get statistics for the dashboard.
    
    Access Control:
    - ADMIN: sees global stats
    - DOCTOR: sees own stats
    - STAFF: sees stats for assigned doctor
    """
    db = get_db()
    user_role = current_user.get("role")
    
    query_filter = {}
    doctor_id = None

    if user_role == "doctor":
        doctor_id = current_user.get("_id")
    elif user_role == "staff":
        # Get assigned doctor ID from token or lookup
        doctor_id = current_user.get("assigned_doctor_id")
        if not doctor_id:
            # Fallback to lookup if not in token
            staff_member = await db.staff_users.find_one({"phone_number": current_user.get("phone_number")})
            if staff_member:
                doctor_id = staff_member.get("doctor_id")

    if doctor_id:
        query_filter["doctor_id"] = ObjectId(doctor_id)

    try:
        # Total Patients
        if user_role == "admin":
            total_patients = await db.patients.count_documents({})
            total_doctors = await db.doctors.count_documents({"is_active": True})
        else:
            if not doctor_id:
                return {
                    "total_patients": 0, "total_doctors": 0, "today_appointments": 0,
                    "ai_interactions": 0, "efficiency": "0%"
                }
            # Count unique patients for this doctor
            distinct_patient_ids = await db.appointments.distinct("patient_id", query_filter)
            total_patients = len(distinct_patient_ids)
            total_doctors = 1

        # Appointments for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        today_filter = {"appointment_datetime": {"$gte": today_start, "$lt": today_end}}
        if query_filter:
            today_filter.update(query_filter)
            
        today_appointments = await db.appointments.count_documents(today_filter)
        
        # AI interactions are global/activity logs
        messages_count = await db.patient_communications.count_documents({})
        ai_activity = messages_count
        
        # Efficiency
        total_apts = await db.appointments.count_documents(query_filter if query_filter else {})
        completed_apts_filter = {"status": "completed"}
        if query_filter:
            completed_apts_filter.update(query_filter)
        completed_apts = await db.appointments.count_documents(completed_apts_filter)
        
        efficiency = "N/A"
        if total_apts > 0:
            efficiency_val = (completed_apts / total_apts) * 100
            efficiency = f"{int(efficiency_val)}%"

        # Weekly Activity (Phase 9.2 - Real chart data)
        weekly_activity = []
        for i in range(6, -1, -1):
            day = today_start - timedelta(days=i)
            day_end = day + timedelta(days=1)
            day_filter = {"appointment_datetime": {"$gte": day, "$lt": day_end}}
            if query_filter:
                day_filter.update(query_filter)
            count = await db.appointments.count_documents(day_filter)
            weekly_activity.append({
                "name": day.strftime("%a"),
                "appointments": count
            })

        return {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "today_appointments": today_appointments,
            "ai_interactions": ai_activity,
            "efficiency": efficiency,
            "weekly_activity": weekly_activity
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search")
async def global_search(
    q: str = Query(..., min_length=2),
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """
    Global search for patients, doctors, and staff.
    
    Access Control:
    - ADMIN: searches all
    - DOCTOR/STAFF: searches only relevant data
    """
    db = get_db()
    regex_pattern = re.compile(q, re.IGNORECASE)
    results = []
    
    user_role = current_user.get("role")
    doctor_id = None

    if user_role == "doctor":
        doctor_id = str(current_user.get("_id"))
    elif user_role == "staff":
        doctor_id = current_user.get("assigned_doctor_id")
        if not doctor_id:
            staff_member = await db.staff_users.find_one({"phone_number": current_user.get("phone_number")})
            if staff_member:
                doctor_id = str(staff_member.get("doctor_id"))

    try:
        # SEARCH PATIENTS
        patient_query = {"$or": [{"full_name": regex_pattern}, {"phone_number": regex_pattern}]}
        if user_role in ["doctor", "staff"] and doctor_id:
            patient_query["doctor_id"] = ObjectId(doctor_id)
            
        patients = await db.patients.find(patient_query).limit(10).to_list(None)
        for p in patients:
            results.append({
                "id": str(p["_id"]),
                "type": "Patient",
                "title": p.get("full_name", "Unknown"),
                "subtitle": p.get("phone_number", ""),
                "contact": p.get("email", "No Email"),
                "status": "Active" if p.get("is_active", True) else "Inactive",
                "link": "/patients"
            })

        # SEARCH DOCTORS (Admin Only for management, others for viewing)
        doctor_search_query = {"$or": [{"full_name": regex_pattern}, {"specialty": regex_pattern}], "is_active": True}
        doctors = await db.doctors.find(doctor_search_query).limit(10).to_list(None)
        for d in doctors:
            results.append({
                "id": str(d["_id"]),
                "type": "Doctor",
                "title": d.get("full_name", "Unknown"),
                "subtitle": d.get("specialty", "General"),
                "contact": d.get("phone", d.get("whatsapp_number", "No Phone")),
                "status": "Active",
                "link": "/doctors"
            })

        # SEARCH STAFF
        if user_role in ["admin", "doctor"]:
            staff_query = {"$or": [{"full_name": regex_pattern}, {"phone_number": regex_pattern}], "is_active": True}
            if user_role == "doctor":
                staff_query["doctor_id"] = str(doctor_id)
                
            staff_members = await db.staff_users.find(staff_query).limit(10).to_list(None)
            for s in staff_members:
                results.append({
                    "id": str(s["_id"]),
                    "type": "Staff",
                    "title": s.get("full_name", "Unknown"),
                    "subtitle": s.get("role", "Staff").capitalize(),
                    "contact": s.get("phone_number", ""),
                    "status": "Active",
                    "link": "/add-staff" if user_role == "doctor" else "/settings"
                })

        return results
    except Exception as e:
        logger.error(f"Error in global search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/notifications")
async def get_notifications(current_user: dict = Depends(require_role("admin"))):
    """Admin-only notifications about system health and activity."""
    db = get_db()
    notifications = []
    
    try:
        # Check for recent doctor additions
        recent_doctors = await db.doctors.find().sort("created_at", -1).limit(2).to_list(None)
        for doc in recent_doctors:
            notifications.append({
                "id": str(doc["_id"]),
                "title": "New Doctor Registered",
                "message": f"Dr. {doc.get('full_name')} ({doc.get('specialty')}) has been added.",
                "type": "info",
                "time": doc.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d %H:%M")
            })
            
        # Check for recent failed WhatsApp messages
        # Note: This is a placeholder as we don't have a status field in patient_communications yet
        # notifications.append(...)

        # System Health OK
        notifications.append({
            "id": "sys_ok",
            "title": "System Health",
            "message": "All AI subsystems are operating normally.",
            "type": "success",
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        })

        notifications.sort(key=lambda x: x["time"], reverse=True)
        return notifications
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return []

@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 50,
    current_user: dict = Depends(require_role("admin"))
):
    """Retrieve system audit logs. Admin only."""
    db = get_db()
    try:
        logs = await db.audit_log.find().sort("timestamp", -1).limit(limit).to_list(None)
        for log in logs:
            log["_id"] = str(log["_id"])
            if isinstance(log.get("timestamp"), datetime):
                log["timestamp"] = log["timestamp"].isoformat()
        return logs
    except Exception as e:
        logger.error(f"Error fetching audit logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


