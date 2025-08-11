from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import shutil
from pathlib import Path

from routes.helper import ensure_user_dirs, mark_as_processed
from db.ingestion import ingest_documents  

router = APIRouter()

class UploadResponse(BaseModel):
    message: str
    files_processed: List[str]

@router.post("/", response_model=UploadResponse)
async def upload_documents(
    user_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    dirs = ensure_user_dirs(user_id)
    saved_files = []

    for file in files:
        file_path = dirs["not_processed_dir"] / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

    await ingest_documents(str(dirs["not_processed_dir"]), user_id)

    for filename in saved_files:
        mark_as_processed(user_id, filename)

    return UploadResponse(
        message="Files uploaded, processed, and moved successfully",
        files_processed=saved_files
    )
