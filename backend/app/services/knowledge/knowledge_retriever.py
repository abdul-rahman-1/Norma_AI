"""
knowledge_retriever.py
----------------------
Retrieves relevant context from the knowledge base to ground AI responses.
Uses keyword search + AI-scored relevance (Gemini Flash).
"""

import logging
import google.generativeai as genai
from app.config import get_settings
from app.services.knowledge.knowledge_store import search_documents
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

async def retrieve_context(query: str, db, category: Optional[str] = None, max_docs: int = 3) -> str:
    """
    Retrieve relevant clinic context for a given query.
    
    1. Search for top 10 matches via keywords/regex.
    2. Use Gemini Flash to select the most relevant chunks.
    3. Assemble into a single context string.
    """
    try:
        # Search documents
        docs = await search_documents(query, category, db)
        if not docs:
            return ""
            
        # If we have only a few, use them all
        if len(docs) <= max_docs:
            context_parts = []
            for d in docs:
                context_parts.append(f"TITLE: {d['title']}\nCONTENT: {d['content']}")
            return "\n\n---\n\n".join(context_parts)

        # Use Gemini to rank/select the most relevant docs
        doc_summaries = []
        for i, d in enumerate(docs):
            snippet = d['content'][:300] + "..." if len(d['content']) > 300 else d['content']
            doc_summaries.append(f"[{i}] {d['title']}: {snippet}")

        ranking_prompt = f"""
Query: "{query}"

Available Knowledge Documents:
{chr(10).join(doc_summaries)}

Task: Identify the top {max_docs} most relevant documents to answer the query.
Return ONLY a comma-separated list of indices.
Example: 0, 2, 5
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(ranking_prompt)
        
        try:
            # Basic parsing of the comma-separated list
            text = response.text.strip()
            # Handle potential markdown formatting if Gemini adds it
            if "```" in text:
                text = text.replace("```", "").strip()
            indices = [int(idx.strip()) for idx in text.split(",") if idx.strip().isdigit()]
            selected_docs = [docs[i] for i in indices if i < len(docs)][:max_docs]
        except Exception as pe:
            logger.warning(f"Failed to parse Gemini ranking ({pe}), falling back to top results.")
            selected_docs = docs[:max_docs]

        context_parts = []
        for d in selected_docs:
            context_parts.append(f"TITLE: {d['title']}\nCONTENT: {d['content']}")
            
        return "\n\n---\n\n".join(context_parts)

    except Exception as e:
        logger.error(f"Context retrieval error: {e}")
        return ""
