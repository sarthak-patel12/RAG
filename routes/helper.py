import os
import shutil
from pathlib import Path
from typing import Union
from db.db_create import create_typesense_collections

BASE_UPLOAD_DIR = Path("user_uploads") 

def delete_document_by_filename(user_id: str, filename: str):
    """
    Deletes all documents in Typesense for a given user where the source contains the filename.
    This matches partial path or just filename.
    """
    client = create_typesense_collections()
    try:
        result = client.collections["documents"].documents.delete({
            "filter_by": f"user_id:={user_id} && source:={filename}"
        })
        print(f"🗑 Deleted {result.get('num_deleted', 0)} docs for user={user_id}, filename={filename}")
        return result
    except Exception as e:
        print(f"Error deleting docs for {filename}: {e}")
        return None


def ensure_user_dirs(user_id: str) -> dict:
    """
    Ensures that the folder structure exists for the user.
    Returns dict with paths to main, processed, and not_processed folders.
    """
    user_dir = BASE_UPLOAD_DIR / user_id
    processed_dir = user_dir / "processed"
    not_processed_dir = user_dir / "not_processed"

    for path in [processed_dir, not_processed_dir]:
        path.mkdir(parents=True, exist_ok=True)

    return {
        "user_dir": user_dir,
        "processed_dir": processed_dir,
        "not_processed_dir": not_processed_dir,
    }


def save_to_not_processed(user_id: str, file_path: Union[str, Path]) -> Path:
    """
    Saves a file into the user's not_processed folder.
    If a duplicate exists in either folder, replaces it and deletes old records in Typesense.
    """
    dirs = ensure_user_dirs(user_id)
    filename = Path(file_path).name

    for folder in [dirs["processed_dir"], dirs["not_processed_dir"]]:
        existing_file = folder / filename
        if existing_file.exists():
            print(f"[INFO] Duplicate found: {filename}. Replacing old file.")
            existing_file.unlink(missing_ok=True)
            delete_document_by_filename(user_id, filename)

    dest_path = dirs["not_processed_dir"] / filename
    shutil.copy(file_path, dest_path)
    return dest_path


def mark_as_processed(user_id: str, filename: str):
    """Moves a file from not_processed to processed."""
    dirs = ensure_user_dirs(user_id)
    src_path = dirs["not_processed_dir"] / filename
    dest_path = dirs["processed_dir"] / filename

    if src_path.exists():
        shutil.move(str(src_path), str(dest_path))
        print(f"[INFO] Moved {filename} → processed folder.")
    else:
        print(f"[WARN] File {filename} not found in not_processed.")


def list_not_processed(user_id: str):
    """List files in the user's not_processed folder."""
    dirs = ensure_user_dirs(user_id)
    return [f for f in os.listdir(dirs["not_processed_dir"]) if os.path.isfile(dirs["not_processed_dir"] / f)]
