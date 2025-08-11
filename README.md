# 📄 Smart Document Q&A System  
**Hybrid Search • Persistent Memory • Context Engineering**

## 🚀 Overview  
This is a **Retrieval-Augmented Generation (RAG)** powered **Smart Document Q&A System** that supports **multi-turn conversations**, **persistent memory**, **hybrid search** (semantic + keyword), and **advanced context engineering**.  
It’s designed for **accurate, citation-aware answers** to complex queries across uploaded documents, following production-grade design principles.

---

## ✨ Features  
- **📂 Multi-Format Document Ingestion** — PDF, DOCX, TXT with chunking & embeddings.  
- **🔍 Hybrid Search** — Weighted combination of semantic (vector) & keyword search via Typesense Multi-Search.  
- **🧠 Persistent Conversation Memory** — Remembers multi-turn Q&A per user.  
- **⚡ Intelligent Caching** — Avoids redundant LLM calls for repeated queries.  
- **🎯 Context Engineering** — Summarizes history to fit context window.  
- **📜 Citation-Aware Answers** — Includes exact source + page references.  
- **⚙️ Modular Architecture** — Clean separation of ingestion, retrieval, AI, and API layers.  

---

## 🛠 Tech Stack  
- **Python 3.10+**  
- **FastAPI** – API layer  
- **Typesense** – Vector + keyword hybrid search  
- **LangChain / LangGraph** – Agent orchestration  
- **Google Gemini** – LLM & embeddings  
- **PyMuPDF (fitz)** – PDF parsing  
- **python-docx** – DOCX reading  
- **Docker** – Self-hosted Typesense server  

---

## 📂 Project Structure  
```
.
├── config.py                   # Environment variables & API keys
├── main.py                     # FastAPI app entry point
│
├── db_create.py                 # Create Typesense collections
├── ingestion.py                 # Async document ingestion
├── ingestion_old.py             # Legacy ingestion version
├── retrieval.py                 # Hybrid search logic
│
├── conversation_manager.py      # Multi-turn memory manager
├── cache_manager.py             # Query result caching
│
├── embeddings.py                # Google embeddings
├── gemini.py                    # Gemini-based Q&A with citations
├── langchain_gemini.py          # LangChain Gemini LLM wrapper
├── langgraph_graph.py           # LangGraph workflow
├── langgraph_nodes.py           # LangGraph nodes (retrieve, answer)
│
├── helper.py                    # File management & cleanup
│
├── upload.py                    # Document upload API
├── response.py                  # Question answering API
│
├── rag.ipynb                    # Jupyter demo notebook
└── pyproject.toml               # Dependencies & metadata
```

---

## ⚙️ Installation & Setup  

### **1️⃣ Clone the repository**
```bash
git clone https://github.com/sarthak-patel12/RAG.git
cd RAG
```

---

### **2️⃣ Start the Typesense server**
```bash
docker run -p 8108:8108   -v/tmp/typesense-data:/data   typesense/typesense:0.24.1   --data-dir /data   --api-key=xyz   --enable-cors
```

---

### **3️⃣ Create a virtual environment & install dependencies**
```bash
uv venv rag
rag\Scripts\activate    # (Windows)
# or source rag/bin/activate (Linux/Mac)

uv pip install -e .
```
In Jupyter Notebook, select the **rag** kernel.

---

### **4️⃣ Set environment variables**
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_key
TYPESENSE_API_KEY=xyz  
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
```

---

### **5️⃣ Run the API**
```bash
uvicorn main:api --reload --port 8000
```

---

## 🔍 API Endpoints  

### **Upload Documents**
`POST /upload`  
Uploads and indexes files for a given user.
```bash
curl -X POST "http://localhost:8000/upload"   -F "user_id=test_user"   -F "files=@/path/to/file.pdf"
```

### **Ask a Question**
`POST /ask`  
Ask a question, get JSON answer with citations.
```bash
curl -X POST "http://localhost:8000/ask"   -H "Content-Type: application/json"   -d '{"user_id":"test_user", "query":"What is the main topic?"}'
```

### **Health Check**
`GET /health`  
Check if service is running.
```bash
curl http://localhost:8000/health
```

---

## 🧠 How It Works  
1. **Document Ingestion**
   - Reads files → Splits into chunks → Embeds with Gemini → Stores in Typesense.  

2. **Query Processing**
   - Checks cache → Retrieves results using hybrid search → Weights and merges scores.  

3. **Answer Generation**
   - Passes retrieved chunks to Gemini with citations → Parses structured JSON output.  

4. **Memory & Context Management**
   - Stores Q&A turns → Summarizes history when context window is near limit.  

---

## 🧪 Demo  
Open **`rag.ipynb`** and follow the step-by-step cells to ingest documents and run queries interactively.

---

## 📌 Future Improvements  
- Authentication & multi-user access control  
- Advanced reranking for hybrid search  
- Web-based chat UI with streaming responses  
- Support for more document formats  
