import json

class ConversationManager:
    def __init__(self, client):
        self.client = client

    def get_next_turn_index(self, user_id: str) -> int:
        search = self.client.collections["conversation_memory"].documents.search({
            "q": "*",
            "query_by": "query",
            "filter_by": f"user_id:={user_id}",
            "sort_by": "turn_index:desc",
            "per_page": 1
        })
        if search["hits"]:
            return search["hits"][0]["document"]["turn_index"] + 1
        return 1

    def save_turn(self, user_id: str, query: str, answer: dict):
        idx = self.get_next_turn_index(user_id)
        doc_id = f"{user_id}_{idx}"
        self.client.collections["conversation_memory"].documents.upsert({
            "id": doc_id,
            "user_id": user_id,
            "turn_index": idx,
            "query": query,
            "answer_json": json.dumps(answer)
        })

    def get_conversation_history(self, user_id: str, last_n: int = 5):
        search = self.client.collections["conversation_memory"].documents.search({
            "q": "*",
            "query_by": "query",
            "filter_by": f"user_id:={user_id}",
            "sort_by": "turn_index:asc",
            "per_page": last_n
        })
        history = []
        for hit in search["hits"]:
            doc = hit["document"]
            try:
                answer = json.loads(doc["answer_json"])
            except:
                answer = {"content": None, "citations": {}}
            history.append({"query": doc["query"], "answer": answer})
        return history
