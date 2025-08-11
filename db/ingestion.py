import os
import uuid
import fitz
import asyncio
from docx import Document
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.embeddings import get_text_embedding

from concurrent.futures import ThreadPoolExecutor
from db.db_create import db_client


client = db_client.get_client()


def read_pdf_by_page(file_path):
    try:
        doc = fitz.open(file_path)
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text("text") or ""
            yield page_number, text, False
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")

def read_docx(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        yield 1, text, True
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")

def read_txt(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        yield 1, text, True
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")


async def process_chunk(chunk_data, executor):
    """Embed and insert a single chunk asynchronously."""
    chunk, file_path, page_number, synthetic, user_id = chunk_data
    file_path = file_path.replace("not_processed", "processed")
    if not chunk.strip():
        return None

    try:
        embedding = await asyncio.to_thread(get_text_embedding, chunk)
        document = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "content": chunk,
            "embedding": embedding,
            "source": file_path,
            "page_number": page_number,
            "synthetic_page": synthetic
        }
        await asyncio.to_thread(client.collections["documents"].documents.upsert, document)
        return True
    except Exception as e:
        print(f"Error processing chunk from {file_path}, page {page_number}: {e}")
        return False

async def ingest_documents(folder_path: str, user_id: str):
    """Async-parallel ingestion of all documents in a folder."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    tasks = []

    executor = ThreadPoolExecutor(max_workers=8)

    for file_name in os.listdir(folder_path):
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

        synthetic_page_counter = 1
        for page_number, text, synthetic in pages or []:
            chunks = splitter.split_text(text)
            for chunk in chunks:
                page_num_to_use = synthetic_page_counter if synthetic else page_number
                tasks.append(process_chunk((chunk, file_path, page_num_to_use, synthetic, user_id), executor))
                if synthetic:
                    synthetic_page_counter += 1

    results = await asyncio.gather(*tasks)
    success_count = sum(1 for r in results if r)
    print(f"✅ Ingested {success_count} chunks from folder {folder_path} for user {user_id}")
