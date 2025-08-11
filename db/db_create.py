import typesense
from config import TYPESENSE_HOST, TYPESENSE_PORT, TYPESENSE_PROTOCOL, TYPESENSE_API_KEY

class create_typesense_collections():
    def __init__(self):
        """
        Creates all required Typesense collections if they don't exist:
        - documents
        - conversation_memory
        - qa_cache
        """

        collections = [
            {
                "name": "documents",
                "fields": [
                    {"name": "id", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "content", "type": "string"},
                    {"name": "embedding", "type": "float[]", "num_dim": 768},
                    {"name": "source", "type": "string"},
                    {"name": "page_number", "type": "int32"},
                    {"name": "synthetic_page", "type": "bool", "optional": True}
                ],
                "default_sorting_field": "page_number"
            },
            {
                "name": "conversation_memory",
                "fields": [
                    {"name": "id", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "turn_index", "type": "int32"},
                    {"name": "query", "type": "string"},
                    {"name": "answer_json", "type": "string"}
                ],
                "default_sorting_field": "turn_index"
            },
            {
                "name": "qa_cache",
                "fields": [
                    {"name": "id", "type": "string"},
                    {"name": "user_id", "type": "string"},
                    {"name": "query", "type": "string"},
                    {"name": "retrieved_chunks_json", "type": "string"},
                    {"name": "answer_json", "type": "string"}
                ]
            }
        ]
        client = typesense.Client({
            'nodes': [{'host': TYPESENSE_HOST, 'port': TYPESENSE_PORT, 'protocol': TYPESENSE_PROTOCOL}],
            'api_key': TYPESENSE_API_KEY,
            'connection_timeout_seconds': 5
        })
        for schema in collections:
            try:
                client.collections.create(schema)
                print(f"✅ Created Typesense collection: {schema['name']}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"ℹ Collection {schema['name']} already exists")
                else:
                    raise

    def get_client(self):
        client = typesense.Client({
            'nodes': [{'host': TYPESENSE_HOST, 'port': TYPESENSE_PORT, 'protocol': TYPESENSE_PROTOCOL}],
            'api_key': TYPESENSE_API_KEY,
            'connection_timeout_seconds': 5
        })
        return client
    
db_client = create_typesense_collections()