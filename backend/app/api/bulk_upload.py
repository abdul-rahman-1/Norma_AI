"""
bulk_upload.py
--------------
Universal bulk upload API endpoints.
Provides /preview for validation and duplicate detection,
and /commit for final DB execution.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from app.core.security import require_role
from app.db.mongodb import get_db
from app.services.ingestion.type_detector import detect_entity_type
from app.services.ingestion.column_mapper import map_columns
from app.services.ingestion.validators import validate_row
from app.services.ingestion.duplicate_checker import check_duplicate
from app.services.ingestion.entity_writers import write_record
from datetime import datetime
from bson import ObjectId
import pandas as pd
import os
import shutil
import uuid
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bulk", tags=["bulk"])

@router.post("/preview")
async def bulk_preview(
    file: UploadFile = File(...),
    entity_type_override: str = Body(None),
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin", "doctor", "staff", "receptionist"))
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")
    
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    job_id = str(uuid.uuid4())
    file_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        df = pd.read_excel(file_path)
        columns = df.columns.tolist()
        
        # Detect entity type
        entity_type = detect_entity_type(columns, sheet_name=file.filename, explicit_override=entity_type_override)
        
        # Map columns using AI
        sample_rows = df.head(3).to_dict(orient='records')
        mapping = await map_columns(columns, sample_rows, entity_type)
        
        preview_rows = []
        errors = []
        duplicates = []
        
        summary = {
            "total_rows": len(df),
            "valid": 0,
            "invalid": 0,
            "duplicates": 0,
            "new": 0
        }
        
        # Process rows for preview
        limit = min(len(df), 100)
        
        for index, row in df.iterrows():
            # Map row to schema
            record = {}
            for schema_field, excel_col in mapping.items():
                if excel_col and excel_col in df.columns:
                    val = row[excel_col]
                    if pd.isna(val): val = None
                    record[schema_field] = val
            
            # Validate
            row_errors = validate_row(entity_type, record, index + 2)
            if row_errors:
                summary["invalid"] += 1
                if index < limit:
                    for err in row_errors:
                        errors.append({"row": err.row, "field": err.field, "reason": err.reason})
                continue
            
            # Check duplicates
            dup_result = await check_duplicate(entity_type, record, db)
            if dup_result.is_duplicate:
                summary["duplicates"] += 1
                if index < limit:
                    duplicates.append({
                        "row": index + 2,
                        "existing_id": dup_result.existing_id,
                        "key": dup_result.matched_key,
                        "record": record
                    })
            else:
                summary["new"] += 1
            
            summary["valid"] += 1
            if index < limit:
                preview_rows.append({
                    "row": index + 2, 
                    "record": record, 
                    "is_duplicate": dup_result.is_duplicate,
                    "matched_key": dup_result.matched_key
                })

        # Log the job in DB
        job = {
            "job_id": job_id,
            "filename": file.filename,
            "entity_type": entity_type,
            "status": "preview",
            "uploaded_by": str(current_user["_id"]) if current_user.get("_id") else "admin",
            "summary": summary,
            "mapping": mapping,
            "file_path": file_path,
            "created_at": datetime.utcnow()
        }
        await db.upload_jobs.insert_one(job)
        
        return {
            "job_id": job_id,
            "entity_type": entity_type,
            "mapping": mapping,
            "summary": summary,
            "preview_rows": preview_rows,
            "errors": errors[:100],
            "duplicates": duplicates[:100]
        }
        
    except Exception as e:
        logger.error(f"Bulk preview error: {e}")
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/commit")
async def bulk_commit(
    job_id: str = Body(..., embed=True),
    overwrite_duplicates: bool = Body(False, embed=True),
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin", "doctor", "staff", "receptionist"))
):
    job = await db.upload_jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job["status"] == "committed":
        raise HTTPException(status_code=400, detail="Job already committed")
        
    file_path = job["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Temporary file lost. Please re-upload.")
        
    try:
        df = pd.read_excel(file_path)
        entity_type = job["entity_type"]
        mapping = job["mapping"]
        
        results = {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0
        }
        
        row_results = []
        
        uploader_context = {
            "_id": str(current_user["_id"]) if current_user.get("_id") else None,
            "role": current_user.get("role")
        }

        for index, row in df.iterrows():
            record = {}
            for schema_field, excel_col in mapping.items():
                if excel_col and excel_col in df.columns:
                    val = row[excel_col]
                    if pd.isna(val): val = None
                    record[schema_field] = val
            
            # Final validation before write
            row_errors = validate_row(entity_type, record, index + 2)
            if row_errors:
                results["errors"] += 1
                if len(row_results) < 500:
                    row_results.append({"row": index + 2, "action": "error", "reason": row_errors[0].reason})
                continue
                
            write_res = await write_record(entity_type, record, index + 2, db, uploader_context, overwrite=overwrite_duplicates)
            
            results[write_res.action] += 1
            if len(row_results) < 500:
                row_results.append({
                    "row": write_res.row,
                    "action": write_res.action,
                    "id": write_res.id,
                    "reason": write_res.reason
                })
            
        # Update job status
        await db.upload_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "committed",
                "results": results,
                "committed_at": datetime.utcnow()
            }}
        )
        
        # Cleanup file
        os.remove(file_path)
        
        return {
            "job_id": job_id,
            "entity_type": entity_type,
            "results": results,
            "row_results": row_results
        }
        
    except Exception as e:
        logger.error(f"Bulk commit error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
