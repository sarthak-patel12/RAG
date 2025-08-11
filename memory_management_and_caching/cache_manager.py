import json
import time
import hashlib


class CacheManager:
    def __init__(self, client):
        self.client = client
        self.collection_name = "qa_cache"

        existing = [c["name"] for c in self.client.collections.retrieve()]
        if self.collection_name not in existing:
            self.client.collections.create({
                "name": self.collection_name,
                "fields": [
                    {"name": "id", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "query", "type": "string"},
                    {"name": "retrieved_chunks_json", "type": "string"},
                    {"name": "answer_json", "type": "string"},
                    {"name": "timestamp", "type": "int64"}
                ]
            })

    def _normalize(self, query: str) -> str:
        return " ".join(query.strip().lower().split())
    
    def _doc_id(self, user_id: str, norm_query: str) -> str:
        """Stable SHA256-based doc ID."""
        query_hash = hashlib.sha256(norm_query.encode("utf-8")).hexdigest()
        return f"{user_id}_{query_hash}"

    def get_cached_result(self, user_id: str, query: str):
        norm_query = self._normalize(query)
        doc_id = self._doc_id(user_id, norm_query)
        try:
            doc = self.client.collections[self.collection_name].documents[doc_id].retrieve()
            print(f"Cache hit for query: '{query}' (norm: '{norm_query}')")
            return json.loads(doc["retrieved_chunks_json"]), json.loads(doc["answer_json"])
        except Exception:
            print(f"Cache miss for query: '{query}' (norm: '{norm_query}')")
            return None, None

    def save_cache(self, user_id: str, query: str, retrieved_chunks: list, answer: dict):
        if not answer or answer.get("content") is None:
            print(f" Not caching empty/None answer for query: '{query}'")
            return

        norm_query = self._normalize(query)
        doc_id = self._doc_id(user_id, norm_query)
        try:
            self.client.collections[self.collection_name].documents.upsert({
                "id": doc_id,
                "user_id": user_id,
                "query": norm_query,
                "retrieved_chunks_json": json.dumps(retrieved_chunks),
                "answer_json": json.dumps(answer),
                "timestamp": int(time.time())
            })
            print(f"Cached result for query: '{query}' (norm: '{norm_query}')")
        except Exception as e:
            print("Cache save error:", e)
