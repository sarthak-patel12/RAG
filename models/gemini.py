import os
import google.generativeai as genai
import re

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-pro")

def ask_gemini_with_citations(query: str, retrieved_chunks: list) -> dict:
    """
    Passes retrieved chunks (with citations) to Gemini.
    Gemini selects and uses citations naturally in the answer.
    Then we extract citations from Gemini's response.
    """

    context_parts = []
    for idx, chunk in enumerate(retrieved_chunks, start=1):
        context_parts.append(f"[{idx}] {chunk['content']} (Source: {chunk['citation']})")

    context_str = "\n\n".join(context_parts)
    
    prompt = f"""
You are a helpful assistant.
You have the following retrieved context, each with a source in parentheses.
Answer the question using the most relevant information and cite sources inline
using their number in square brackets.

Question: {query}

Retrieved Context:
{context_str}

Your answer should be clear, concise, and include citations in the format [number].
"""

    response = model.generate_content(prompt)
    answer_text = response.text.strip()
    #print("Gemini's answer:", answer_text)  #

    citation_nums = re.findall(r"\[(\d+)\]", answer_text)
    citation_nums = sorted(set(int(num) for num in citation_nums if num.isdigit()))


    final_citations = []
    for num in citation_nums:
        if 1 <= num <= len(retrieved_chunks):
            final_citations.append(retrieved_chunks[num-1]["citation"])

    return {
        "answer": answer_text,
        "citations": final_citations
    }
