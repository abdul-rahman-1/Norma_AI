"""
knowledge.py
------------
Knowledge CRUD + query API.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import require_role
from app.db.mongodb import get_db
from app.services.knowledge import knowledge_store, knowledge_retriever
from typing import List, Optional
import google.generativeai as genai
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["knowledge"])
settings = get_settings()

@router.get("", response_model=List[dict])
async def list_knowledge(
    category: Optional[str] = None,
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    return await knowledge_store.list_documents(category, db)

@router.post("")
async def create_knowledge(
    doc: dict = Body(...),
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    doc["created_by"] = current_user.get("_id")
    doc_id = await knowledge_store.upsert_document(doc, db)
    return {"doc_id": doc_id, "status": "success"}

@router.get("/{doc_id}")
async def get_knowledge(
    doc_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    doc = await knowledge_store.get_document(doc_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.patch("/{doc_id}")
async def update_knowledge(
    doc_id: str,
    doc_update: dict = Body(...),
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    doc_update["doc_id"] = doc_id
    await knowledge_store.upsert_document(doc_update, db)
    return {"status": "success"}

@router.delete("/{doc_id}")
async def delete_knowledge(
    doc_id: str,
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    success = await knowledge_store.delete_document(doc_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}

@router.post("/query")
async def query_knowledge(
    question: str = Body(..., embed=True),
    category: Optional[str] = Body(None, embed=True),
    db=Depends(get_db),
    current_user: dict = Depends(require_role("admin", "doctor", "staff"))
):
    """Ask a question grounded in the clinic knowledge base."""
    # Retrieve context
    context = await knowledge_retriever.retrieve_context(question, db, category)
    if not context:
        return {
            "answer": "I couldn't find any specific clinic information regarding that. Please check with the administrator.", 
            "sources": []
        }
        
    # Generate grounded answer
    prompt = f"""
You are a smart clinic operations assistant for Norma AI.
Use the following CLINIC KNOWLEDGE BASE context to answer the user's question.
If the answer is not in the context, say you don't know based on clinic documents.

CONTEXT:
{context}

QUESTION:
{question}

Return a helpful, professional answer grounded in the context.
"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        return {
            "answer": response.text.strip(),
            "sources": ["Clinic Knowledge Base"]
        }
    except Exception as e:
        logger.error(f"Knowledge query generation error: {e}")
        return {"answer": "Error generating answer. Please try again.", "sources": []}
