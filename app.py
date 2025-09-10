
import os
import json
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List

# Configuration
HASH_STORAGE_DIR = "hash_storage"

# Create storage directory if it doesn't exist
if not os.path.exists(HASH_STORAGE_DIR):
    os.makedirs(HASH_STORAGE_DIR)

app = FastAPI(
    title="DocPro Backend",
    description="API for document protection, verification, and data extraction.",
    version="1.0.0",
)

# --- Helper Functions ---

def get_hash_file_path(filename: str) -> str:
    """Generate the path for storing a file's hash data."""
    return os.path.join(HASH_STORAGE_DIR, f"{filename}.json")

# --- API Endpoints ---

@app.post("/protect")
async def protect_document(
    file: UploadFile = File(...),
    secret_data: str = Form(""),
    encrypt_payload: bool = Form(False),
    password: str = Form(None),
    original_hash: str = Form(...)
):
    """
    Protects a single document by storing its hash and embedding metadata.
    (Full steganography logic is not implemented as per client-side focus).
    """
    try:
        filename = file.filename
        hash_file_path = get_hash_file_path(filename)

        protected_hash = original_hash  # Placeholder

        hash_data = {
            "original_file": filename,
            "original_hash": original_hash,
            "protected_hash": protected_hash, # This would be different after protection
            "protection_date": "N/A", # Placeholder
        }

        with open(hash_file_path, 'w') as f:
            json.dump(hash_data, f, indent=4)

        file_content = await file.read()

        return JSONResponse(content={
            "success": True,
            "message": f"'{filename}' protected successfully.",
            "original_file": filename,
            "original_hash": original_hash,
            "protected_hash": protected_hash,
            "protected_filename": f"protected_{filename}",
            "protected_file_data": file_content.hex() # Sending hex to be safe
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Protection failed: {str(e)}")

@app.post("/verify")
async def verify_document(
    file: UploadFile = File(...),
    current_hash: str = Form(...)
):
    """
    Verifies a single document by comparing its hash with the stored hash.
    """
    try:
        filename = file.filename
        hash_file_path = get_hash_file_path(filename)

        if not os.path.exists(hash_file_path):
            return JSONResponse(content={
                "success": True, # Operation succeeded, but file is not verified
                "is_verified": False,
                "message": "Verification failed: No protection data found for this file.",
                "current_hash": current_hash,
                "stored_hash": "N/A"
            })

        with open(hash_file_path, 'r') as f:
            hash_data = json.load(f)

        stored_hash = hash_data.get("protected_hash")
        is_verified = (current_hash == stored_hash)

        return JSONResponse(content={
            "success": True,
            "is_verified": is_verified,
            "message": "Verification complete.",
            "current_hash": current_hash,
            "stored_hash": stored_hash
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.post("/extract")
async def extract_data(
    file: UploadFile = File(...),
    password: str = Form(None)
):
    """
    Extracts embedded data from a document.
    (This is a placeholder as extraction logic is client-side).
    """
    return JSONResponse(content={
        "success": True,
        "message": "Extraction logic is handled client-side.",
        "extracted_data": "(Client-side extraction not implemented in this backend mock)"
    })

@app.post("/batch-protect")
async def batch_protect_documents(
    files: List[UploadFile] = File(...),
    original_hashes: List[str] = Form(...),
    secret_data: str = Form(""),
    encrypt_payload: bool = Form(False),
    password: str = Form(None)
):
    """
    Protects a batch of documents.
    """
    results = []
    for i, file in enumerate(files):
        try:
            original_hash = original_hashes[i]
            # Logic from single protect, simplified
            hash_file_path = get_hash_file_path(file.filename)
            hash_data = {"original_hash": original_hash, "protected_hash": original_hash} # Placeholder
            with open(hash_file_path, 'w') as f:
                json.dump(hash_data, f)
            results.append({"file": file.filename, "status": "success"})
        except Exception as e:
            results.append({"file": file.filename, "status": "error", "error": str(e)})

    return JSONResponse(content={"success": True, "results": results})

@app.post("/batch-verify")
async def batch_verify_documents(
    files: List[UploadFile] = File(...),
    current_hashes: List[str] = Form(...)
):
    """
    Verifies a batch of documents.
    """
    results = []
    for i, file in enumerate(files):
        try:
            current_hash = current_hashes[i]
            hash_file_path = get_hash_file_path(file.filename)
            if not os.path.exists(hash_file_path):
                results.append({"file": file.filename, "status": "error", "error": "Not found"})
                continue
            with open(hash_file_path, 'r') as f:
                hash_data = json.load(f)
            stored_hash = hash_data.get("protected_hash")
            is_verified = (current_hash == stored_hash)
            results.append({"file": file.filename, "status": "success", "is_verified": is_verified, "current_hash": current_hash, "stored_hash": stored_hash})
        except Exception as e:
            results.append({"file": file.filename, "status": "error", "error": str(e)})

    return JSONResponse(content={"success": True, "results": results})


# --- Static File Serving ---

# Serve the main web application files (index.html, app.html, etc.)
app.mount("/", StaticFiles(directory="web", html=True), name="web")

# Serve the static assets (CSS, JS, images)
app.mount("/static", StaticFiles(directory="web/static"), name="static")

@app.get("/")
async def read_root():
    """Serve the main landing page."""
    return FileResponse('web/index.html')

@app.get("/app.html")
async def read_app():
    """Serve the main application page."""
    return FileResponse('web/app.html')

# To run this application:
# uvicorn app:app --reload
