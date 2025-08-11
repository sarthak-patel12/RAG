from langchain_google_genai import ChatGoogleGenerativeAI
import os

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
    streaming=True
)
