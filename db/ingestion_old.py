import os
import uuid
import fitz
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.embeddings import get_text_embedding
from config import TYPESENSE_HOST, TYPESENSE_PORT, TYPESENSE_PROTOCOL, TYPESENSE_API_KEY
import typesense
from main import db_client


client = db_client.get_client()

def read_pdf_by_page(file_path):
    """Yield (page_number, text, is_synthetic=False) for each PDF page."""
    try:
        doc = fitz.open(file_path)
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            yield page_number, text, False  # False = real page
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")

def read_docx(file_path):
    """Yield synthetic pages from DOCX."""
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        yield 1, text, True  # True = synthetic page
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")

def read_txt(file_path):
    """Yield synthetic pages from TXT."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        yield 1, text, True
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")

def ingest_documents(folder_path: str, user_id: str):
    """Ingest documents from a folder into Typesense."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    for file_name in os.listdir(folder_path):
        try:
            file_path = os.path.join(folder_path, file_name)

            if file_name.lower().endswith(".pdf"):
                pages = read_pdf_by_page(file_path)
            elif file_name.lower().endswith(".docx"):
                pages = read_docx(file_path)
            elif file_name.lower().endswith(".txt"):
                pages = read_txt(file_path)
            else:
                print(f"Skipping unsupported file: {file_name}")
                continue

            for page_number, text, synthetic in pages or []:
                chunks = splitter.split_text(text)
                synthetic_page_counter = 1

                for chunk in chunks:
                    if not chunk.strip():
                        continue
                    try:
                        embedding = get_text_embedding(chunk)
                        document = {
                            "id": str(uuid.uuid4()),
                            "user_id": user_id,
                            "content": chunk,
                            "embedding": embedding,
                            "source": file_path,
                            "page_number": synthetic_page_counter if synthetic else page_number,
                            "synthetic_page": synthetic
                        }
                        client.collections["documents"].documents.upsert(document)
                        if synthetic:
                            synthetic_page_counter += 1
                    except Exception as embed_err:
                        print(f"Error embedding or inserting chunk from {file_name} page {page_number}: {embed_err}")

            print(f"✅ Ingested: {file_name} for user {user_id}")
        except Exception as file_err:
            print(f"Error processing file {file_name}: {file_err}")
