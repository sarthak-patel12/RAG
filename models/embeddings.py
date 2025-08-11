import google.generativeai as genai
from config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def get_text_embedding(text: str):
    """
    Generate text embedding using Google Generative AI embeddings.
    Returns a list of embeddings.
    """
    model = "models/text-embedding-004"  
    result = genai.embed_content(model=model, content=text)
    return result["embedding"]
