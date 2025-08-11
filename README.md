



#DEMO

Clone the repository 
```bash
gitclone git clone https://github.com/sarthak-patel12/RAG.git
```

Open the ipynb notebook so run the Demo in spetwise

## 📌 Prerequisites for Demo

Before running this demo, please ensure the following setup steps are completed:

---

#### **1 Start the Typesense server**

- Install Docker Desktop

We use **Typesense** for document indexing and retrieval.

```bash
docker run -p 8108:8108 \
  -v/tmp/typesense-data:/data \
  typesense/typesense:0.24.1 \
  --data-dir /data \
  --api-key=xyz \
  --enable-cors
```

#### **2 Create virtual environment and insatll dependecies**

```bash
uv venv rag

rag\Scripts\activate #(for windows)

uv pip install -e .
```
- In the top right corner select kernel as rag

#### **3 Set the .env file and run the Rag api**

- Get the gemini api key and set this in you .env(change the typesense variables if you have changed in the above docker run)
GEMINI_API_KEY=
TYPESENSE_API_KEY=xyz  
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
```bash
uvicorn main:api --reload --port 8000
```
