from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any

from db.db_create import create_typesense_collections
from memory_management_and_caching.conversation_manager import ConversationManager
from memory_management_and_caching.cache_manager import CacheManager
from models.langgraph_graph import app

#client = create_typesense_collections()
#conv_manager = ConversationManager(client)
#cache_manager = CacheManager(client)

router = APIRouter()

class AskRequest(BaseModel):
    user_id: str
    query: str

@router.post("/", response_model=Dict[str, Any])
async def ask_question(req: AskRequest):
    """Answer a user question using RAG pipeline with memory + caching."""
    state = {"query": req.query, "user_id": req.user_id}

    final_answer = {}
    async for step in app.astream(state):
        if "generate" in step and "answer" in step["generate"]:
            final_answer = step["generate"]["answer"]

    return {"answer": final_answer}
