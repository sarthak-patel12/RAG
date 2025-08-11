from models.embeddings import get_text_embedding
from db.db_create import db_client

client = db_client.get_client()

def multi_search_custom_merge(query: str, user_id: str, top_k: int = 5, keyword_weight: float = 0.4, vector_weight: float = 0.6):
    """Hybrid search using Typesense Multi-Search + client-side weighted merge."""
    embedding = get_text_embedding(query)

    multi_results = client.multi_search.perform({
        "searches": [
            {
                "collection": "documents",
                "q": query,
                "query_by": "content",
                "filter_by": f"user_id:={user_id}",
                "per_page": top_k
            },
            {
                "collection": "documents",
                "q": "*",
                "vector_query": f"embedding:([{','.join(map(str, embedding))}], k:{top_k})",
                "filter_by": f"user_id:={user_id}",
                "per_page": top_k
            }
        ]
    })

    keyword_hits = {hit["document"]["id"]: hit for hit in multi_results["results"][0]["hits"]}
    vector_hits = {hit["document"]["id"]: hit for hit in multi_results["results"][1]["hits"]}

    merged_scores = {}
    for doc_id in set(keyword_hits.keys()) | set(vector_hits.keys()):
        keyword_score = keyword_hits.get(doc_id, {}).get("text_match", 0)
        vector_score = vector_hits.get(doc_id, {}).get("vector_distance", 1)  # smaller is better
        vector_score = 1 - vector_score if vector_score <= 1 else 0  # normalize
        merged_score = (keyword_weight * keyword_score) + (vector_weight * vector_score)
        merged_scores[doc_id] = merged_score

    sorted_docs = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)

    results_with_citations = []
    for doc_id, score in sorted_docs[:top_k]:
        doc = keyword_hits.get(doc_id, vector_hits.get(doc_id))["document"]
        page_label = (
            f"Page {doc['page_number']}"
            if not doc.get("synthetic_page")
            else f"Synthetic Page {doc['page_number']}"
        )
        citation = f"{doc['source']} ({page_label})"
        results_with_citations.append({
            "content": doc["content"],
            "citation": citation,
            "score": score
        })

    return results_with_citations


def multi_search_builtin(query: str, user_id: str, top_k: int = 5):
    """Hybrid search using Typesense Multi-Search with built-in ranking (keyword + vector separately)."""
    embedding = get_text_embedding(query)

    multi_results = client.multi_search.perform({
        "searches": [
            {
                "collection": "documents",
                "q": query,
                "query_by": "content",
                "filter_by": f"user_id:={user_id}",
                "per_page": top_k
            },
            {
                "collection": "documents",
                "q": "*",
                "vector_query": f"embedding:([{','.join(map(str, embedding))}], k:{top_k})",
                "filter_by": f"user_id:={user_id}",
                "per_page": top_k
            }
        ]
    })

    results_with_citations = []
    for result in multi_results["results"]:
        for hit in result["hits"]:
            doc = hit["document"]
            page_label = (
                f"Page {doc['page_number']}"
                if not doc.get("synthetic_page")
                else f"Synthetic Page {doc['page_number']}"
            )
            citation = f"{doc['source']} ({page_label})"
            results_with_citations.append({
                "content": doc["content"],
                "citation": citation,
                "score": hit.get("text_match", 0)
            })

    return results_with_citations
