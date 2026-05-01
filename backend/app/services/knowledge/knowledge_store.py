"""
knowledge_store.py
------------------
CRUD operations for the clinic knowledge base (RAG).
Stores policies, templates, bios, and rules in MongoDB.
"""

from bson import ObjectId
from datetime import datetime
import uuid
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

async def upsert_document(doc: dict, db) -> str:
    """Create or update a knowledge document."""
    doc_id = doc.get("doc_id") or str(uuid.uuid4())
    
    existing = await db.knowledge_documents.find_one({"doc_id": doc_id})
    
    update_data = {
        "category": doc.get("category"),
        "title": doc.get("title"),
        "content": doc.get("content"),
        "tags": doc.get("tags", []),
        "language": doc.get("language", "en"),
        "is_active": doc.get("is_active", True),
        "updated_at": datetime.utcnow()
    }
    
    if not existing:
        update_data["doc_id"] = doc_id
        update_data["created_at"] = datetime.utcnow()
        update_data["created_by"] = doc.get("created_by")
        await db.knowledge_documents.insert_one(update_data)
        return doc_id
    else:
        await db.knowledge_documents.update_one({"doc_id": doc_id}, {"$set": update_data})
        return doc_id

async def get_document(doc_id: str, db) -> Optional[dict]:
    doc = await db.knowledge_documents.find_one({"doc_id": doc_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

async def list_documents(category: Optional[str], db) -> List[dict]:
    query = {"is_active": True}
    if category:
        query["category"] = category
    
    cursor = db.knowledge_documents.find(query).sort("created_at", -1)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs

async def delete_document(doc_id: str, db) -> bool:
    result = await db.knowledge_documents.update_one(
        {"doc_id": doc_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0

async def search_documents(query: str, category: Optional[str], db) -> List[dict]:
    """Search for relevant knowledge documents."""
    search_query = {"is_active": True}
    if category:
        search_query["category"] = category
        
    if query:
        search_query["$or"] = [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}}
        ]
        
    cursor = db.knowledge_documents.find(search_query).limit(10)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)
    return docs
