from typing import TypedDict, List, Dict, Any
from models.langchain_gemini import gemini_llm  
from db.retrieval import multi_search_custom_merge
from memory_management_and_caching.conversation_manager import ConversationManager
from memory_management_and_caching.cache_manager import CacheManager
from db.db_create import db_client
import json
import re

client = db_client.get_client()
conv_manager = ConversationManager(client)
cache_manager = CacheManager(client)

class ConversationState(TypedDict):
    query: str
    original_query: str
    user_id: str
    retrieved_chunks: List[Dict[str, Any]]
    answer: Dict[str, Any]  
    _cache_hit: bool

def summarize_context(history: List[Dict[str, Any]], max_chars: int = 800) -> str:
    """
    Summarizes conversation history to fit into context.
    Falls back to truncation if LLM summarization fails.
    """
    if not history:
        return ""

    transcript = "\n".join(
        f"Q: {h['query']}\nA: {h['answer'].get('content')}" for h in history
    )

    if len(transcript) <= max_chars:
        return transcript

    try:
        prompt = (
            """
            you are a smart summerizer agent that summerizes a conversation accect only the last Q and A.
            Summarize the important facts from this conversation in under 5 sentences only keep the last Q and A in same format:
            \n"""
            f"{transcript}"
        )
        resp = gemini_llm(prompt)
        print("Summarization response:", resp)
        return getattr(resp, "content", str(resp))[:max_chars]
    except Exception as e:
        print("Summarization failed:", e)
        return transcript[:max_chars]


def retrieve(state: ConversationState) -> ConversationState:
    query = state.get("query", "").strip()
    state["original_query"] = query
    user_id = state.get("user_id")
    state["_cache_hit"] = False
    #print(state)
    cached_chunks, cached_answer = cache_manager.get_cached_result(user_id, query)
    #print(cached_chunks, cached_answer)
    if cached_chunks and cached_answer:
        
        state["retrieved_chunks"] = cached_chunks
        state["answer"] = cached_answer
        state["_cache_hit"] = True
        
        return state

    history = conv_manager.get_conversation_history(user_id, last_n=5)
    summary = summarize_context(history)
    augmented_query = f"{summary}\nUser question: {query}" if summary else query
    print("Augmented query:", augmented_query)
    results = multi_search_custom_merge(augmented_query, user_id=user_id, top_k=5)
    print("Results:", results)
    state["query"] = augmented_query
    state["retrieved_chunks"] = results or []
    return state


async def generate_answer(state: ConversationState):
    """
    Generates a JSON answer based ONLY on retrieved context.
    Keeps original strict JSON-with-citations format.
    """
    user_id = state.get("user_id")
    
    if state.get("_cache_hit"):
        
        yield {"answer": state["answer"]}
        return

    context_parts = [
        f"[{i+1}] {chunk['content']} (Source: {chunk['citation']})"
        for i, chunk in enumerate(state.get("retrieved_chunks", []))
    ]
    context_str = "\n\n".join(context_parts)
    print(state["query"])
    print(context_str)
    prompt = f"""
You are a helpful assistant that answers ONLY based on the retrieved context from a RAG system.

Your task:
1. Read the retrieved context below.
2. If the context contains relevant information, use ONLY that information to answer.
3. If there is no relevant information in the context, respond with:
   {{
     "content": null,
     "citations": {{}}
   }}
4. If the question has conversation history, and the latest question is about the history like (summberize the conversation, what is previous question), use ONLY the conversation history to answer and provide empty citations.

Response format:
Output ONLY a valid JSON object with:
- "content": a concise, well-written answer based ONLY on the retrieved context.
- "citations": a dictionary where each key is the document path and the value is a list of page numbers.

Example:
{{
  "content": "The time value of money states that a dollar today is worth more than a dollar in the future due to its earning potential.",
  "citations": {{"finance_700_words.pdf": [3], "finance_200_words.txt": [1]}}
}}
{{
  "content": "summary of previous conversation.",
  "citations": 
}}

Question: {state['query']}

Retrieved Context:
{context_str}

Remember:
- Only use facts from the retrieved context.
- Do not add outside knowledge.
- Output ONLY valid JSON. No text before or after the JSON object.
"""

    chunks = []

    async for msg_chunk in gemini_llm.astream(prompt):
        if hasattr(msg_chunk, "content"):
            chunks.append(msg_chunk.content)
            yield {"answer_partial": "".join(chunks)}

    raw_text = "".join(chunks).strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        parsed = json.loads(json_match.group(0)) if json_match else {"content": None, "citations": {}}

    conv_manager.save_turn(user_id, state.get("original_query", ""), parsed)
    cache_manager.save_cache(user_id, state.get("original_query", ""), state.get("retrieved_chunks", []), parsed)

    yield {"answer": parsed}
