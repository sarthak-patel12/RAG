from fastapi import FastAPI
import uvicorn
from routes import upload, response

api = FastAPI(title="Smart Document Q&A", version="1.0.0")

api.include_router(response.router, prefix="/ask", tags=["Question Answering"])
api.include_router(upload.router, prefix="/upload", tags=["Document Upload"])


@api.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:api", host="0.0.0.0", port=8000, reload=True)
