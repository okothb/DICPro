"""
DocProject API - REST API for Document Protection and Verification
Provides programmatic access to document steganography and verification features.
"""

import base64
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from core.encryptor import DocumentEncryptor
from core.hash_generator import HashGenerator
from core.db import execute_query, setup_database
from core.path_validator import validate_folder_path, sanitize_path_for_display
from core.security import scan_file
from core.security_validator import validate_secret_data, validate_extracted_data
from core.steganography import DocumentSteganography
from core.offline_hash_manager import OfflineHashManager
from api_hash_endpoints import integrate_hash_endpoints

# Initialize FastAPI app
app = FastAPI(
    title="DocProject API",
    description="REST API for Document Protection and Verification using Steganography",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
steg = DocumentSteganography()
hash_gen = HashGenerator()
encryptor = DocumentEncryptor()
offline_hash_manager = OfflineHashManager()

# Pydantic models for request/response
class ProtectionRequest(BaseModel):
    secret_data: str = Field(..., description="Secret data to embed in the document")
    encrypt_payload: bool = Field(False, description="Whether to encrypt the payload")
    password: Optional[str] = Field(None, description="Encryption password (required if encrypt_payload is True)")

class ProtectionResponse(BaseModel):
    success: bool
    message: str
    original_file: str
    protected_filename: str
    protected_file_data: str
    method: str
    original_hash: str
    protected_hash: str
    processing_time: float

class VerificationResponse(BaseModel):
    success: bool
    message: str
    file_path: str
    is_verified: bool
    current_hash: str
    stored_hash: str
    extracted_data: Optional[str] = None

class ExtractionResponse(BaseModel):
    success: bool
    message: str
    file_path: str
    extracted_data: str
    original_hash: str
    protected_hash: str
    hashes_match: bool

class BatchResponse(BaseModel):
    success: bool
    message: str
    total_files: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

# Temporary storage for processing
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

def cleanup_temp_files():
    """Clean up temporary files older than 1 hour"""
    current_time = datetime.now()
    for file_path in TEMP_DIR.glob("*"):
        if file_path.is_file():
            file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age.total_seconds() > 3600:  # 1 hour
                try:
                    file_path.unlink()
                except:
                    pass

@app.on_event("startup")
async def startup_event():
    """Initialize API on startup"""
    cleanup_temp_files()
    # Initialize DB if available
    try:
        setup_database()
    except Exception:
        pass
    
    # Integrate hash management endpoints
    integrate_hash_endpoints(app)
    
    # Create output/hash directory
    os.makedirs("output/hash", exist_ok=True)
    print("✅ Offline-first hash storage initialized")

@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "message": "DocProject API - Document Protection and Verification",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        components={
            "steganography": "active",
            "hash_generator": "active",
            "encryptor": "active"
        }
    )

@app.post("/protect", response_model=ProtectionResponse)
async def protect_document(
    file: UploadFile = File(...),
    secret_data: str = Form(...),
    encrypt_payload: bool = Form(False),
    password: Optional[str] = Form(None)
):
    """
    Protect a single document by embedding secret data using steganography.
    The protected file is returned directly and not stored on the server.
    """
    temp_input = None
    temp_output = None
    try:
        if encrypt_payload and not password:
            raise HTTPException(status_code=400, detail="Password required when encryption is enabled")
        
        # Create temporary input file
        temp_input = TEMP_DIR / f"input_{uuid.uuid4()}_{file.filename}"
        
        # Determine temporary output path
        base_name = Path(file.filename).stem
        ext = Path(file.filename).suffix.lower()
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            output_filename = f"{base_name}_protected.png"
        else:
            output_filename = f"{base_name}_protected{ext}"
        temp_output = TEMP_DIR / output_filename
        
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        is_safe, reason = scan_file(str(temp_input))
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"File rejected: {reason}")
        
        is_valid, error_message = validate_secret_data(secret_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Secret data validation failed: {error_message}")
        
        user_secret = secret_data.encode('utf-8')
        original_hash = hash_gen.generate_file_hash(str(temp_input))
        
        start_time = datetime.now()
        
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            result = steg.hide_data_in_image(str(temp_input), user_secret, str(temp_output), original_hash=original_hash)
        elif ext == ".pdf":
            result = steg.hide_data_in_pdf(str(temp_input), user_secret, str(temp_output), original_hash=original_hash)
        elif ext in [".xlsx", ".xls", ".csv"]:
            result = steg.hide_data_in_excel(str(temp_input), user_secret, str(temp_output))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if result and result.get('success'):
            protected_hash = hash_gen.generate_file_hash(str(temp_output))

            with open(temp_output, "rb") as f:
                protected_file_data = base64.b64encode(f.read()).decode('utf-8')
            
            try:
                offline_hash_manager.store_hash_offline(
                    original_filename=file.filename,
                    original_hash=original_hash,
                    protected_hash=protected_hash,
                    secret_data=user_secret,
                    protection_method=result.get('method', 'unknown'),
                    file_size=temp_input.stat().st_size
                )
            except Exception as e:
                print(f"⚠️ Offline hash storage failed: {e}")

            return ProtectionResponse(
                success=True,
                message="Document protected successfully",
                original_file=file.filename,
                protected_filename=output_filename,
                protected_file_data=protected_file_data,
                method=result.get('method', 'unknown'),
                original_hash=original_hash,
                protected_hash=protected_hash,
                processing_time=processing_time
            )
        else:
            raise HTTPException(status_code=500, detail=f"Protection failed: {result.get('error', 'Unknown error')}")
            
    finally:
        if temp_input and temp_input.exists():
            temp_input.unlink()
        if temp_output and temp_output.exists():
            temp_output.unlink()

@app.post("/verify", response_model=VerificationResponse)
async def verify_document(file: UploadFile = File(...)):
    """
    Verify a protected document's integrity
    """
    temp_file = None
    try:
        temp_file = TEMP_DIR / f"verify_{uuid.uuid4()}_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        is_safe, reason = scan_file(str(temp_file))
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"File rejected: {reason}")
        
        ext = Path(file.filename).suffix.lower()
        
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            result = steg.extract_data_from_image(str(temp_file))
        elif ext == ".pdf":
            result = steg.extract_data_from_pdf(str(temp_file))
        elif ext in [".xlsx", ".xls", ".csv"]:
            result = steg.extract_data_from_excel(str(temp_file))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        
        if result and result.get('success'):
            current_hash = hash_gen.generate_file_hash(str(temp_file))
            
            verification_result = offline_hash_manager.verify_document_offline(
                filename=file.filename,
                current_hash=current_hash
            )
            
            extracted_data = None
            if result.get('secret_data'):
                is_valid, error_message = validate_extracted_data(result['secret_data'])
                if is_valid:
                    extracted_data = result['secret_data'].decode('utf-8', errors='ignore')
                else:
                    extracted_data = f"[SECURITY WARNING: Malicious content detected - {error_message}]"
            
            return VerificationResponse(
                success=True,
                message=verification_result['message'],
                file_path=file.filename,
                is_verified=verification_result['verified'],
                current_hash=current_hash,
                stored_hash=verification_result['stored_hash'] or "No stored hash found",
                extracted_data=extracted_data
            )
        else:
            return VerificationResponse(
                success=False,
                message="Verification failed: Could not extract data.",
                file_path=file.filename,
                is_verified=False,
                current_hash=hash_gen.generate_file_hash(str(temp_file)),
                stored_hash="N/A"
            )
            
    finally:
        if temp_file and temp_file.exists():
            temp_file.unlink()

@app.post("/extract", response_model=ExtractionResponse)
async def extract_data(file: UploadFile = File(...)):
    """
    Extract embedded data from a protected document
    """
    temp_file = None
    try:
        temp_file = TEMP_DIR / f"extract_{uuid.uuid4()}_{file.filename}"
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        is_safe, reason = scan_file(str(temp_file))
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"File rejected: {reason}")
        
        ext = Path(file.filename).suffix.lower()
        
        if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            result = steg.extract_data_from_image(str(temp_file))
        elif ext == ".pdf":
            result = steg.extract_data_from_pdf(str(temp_file))
        elif ext in [".xlsx", ".xls", ".csv"]:
            result = steg.extract_data_from_excel(str(temp_file))
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        
        if result and result.get('success'):
            current_hash = hash_gen.generate_file_hash(str(temp_file))
            verification_result = offline_hash_manager.verify_document_offline(
                filename=file.filename,
                current_hash=current_hash
            )
            
            extracted_data = ""
            if result.get('secret_data'):
                is_valid, error_message = validate_extracted_data(result['secret_data'])
                if is_valid:
                    extracted_data = result['secret_data'].decode('utf-8', errors='ignore')
                else:
                    extracted_data = f"[SECURITY WARNING: Malicious content detected - {error_message}]"
            
            return ExtractionResponse(
                success=True,
                message="Data extracted successfully",
                file_path=file.filename,
                extracted_data=extracted_data,
                original_hash=current_hash,
                protected_hash=verification_result['stored_hash'] or "No stored hash found",
                hashes_match=verification_result['verified']
            )
        else:
            raise HTTPException(status_code=500, detail=f"Extraction failed: {result.get('error', 'Unknown error')}")
            
    finally:
        if temp_file and temp_file.exists():
            temp_file.unlink()

@app.post("/batch-protect", response_model=BatchResponse)
async def batch_protect_documents(
    files: List[UploadFile] = File(...),
    secret_data: str = Form(...),
    encrypt_payload: bool = Form(False),
    password: Optional[str] = Form(None)
):
    """
    Protect multiple documents in batch. Protected files are returned directly.
    """
    if encrypt_payload and not password:
        raise HTTPException(status_code=400, detail="Password required when encryption is enabled")
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        temp_input = None
        temp_output = None
        try:
            temp_input = TEMP_DIR / f"batch_input_{uuid.uuid4()}_{file.filename}"
            
            base_name = Path(file.filename).stem
            ext = Path(file.filename).suffix.lower()
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                output_filename = f"{base_name}_protected.png"
            else:
                output_filename = f"{base_name}_protected{ext}"
            temp_output = TEMP_DIR / output_filename
            
            with open(temp_input, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            is_safe, reason = scan_file(str(temp_input))
            if not is_safe:
                results.append({"file": file.filename, "status": "failed", "error": f"File rejected: {reason}"})
                failed += 1
                continue
            
            is_valid, error_message = validate_secret_data(secret_data)
            if not is_valid:
                results.append({"file": file.filename, "status": "failed", "error": f"Secret data validation failed: {error_message}"})
                failed += 1
                continue
            
            user_secret = secret_data.encode('utf-8')
            original_hash = hash_gen.generate_file_hash(str(temp_input))
            
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                result = steg.hide_data_in_image(str(temp_input), user_secret, str(temp_output), original_hash=original_hash)
            elif ext == ".pdf":
                result = steg.hide_data_in_pdf(str(temp_input), user_secret, str(temp_output), original_hash=original_hash)
            elif ext in [".xlsx", ".xls", ".csv"]:
                result = steg.hide_data_in_excel(str(temp_input), user_secret, str(temp_output))
            else:
                result = None
            
            if result and result.get('success'):
                protected_hash = hash_gen.generate_file_hash(str(temp_output))

                with open(temp_output, "rb") as f:
                    protected_file_data = base64.b64encode(f.read()).decode('utf-8')
                
                try:
                    offline_hash_manager.store_hash_offline(
                        original_filename=file.filename,
                        original_hash=original_hash,
                        protected_hash=protected_hash,
                        secret_data=user_secret,
                        protection_method=result.get('method', 'unknown'),
                        file_size=temp_input.stat().st_size
                    )
                except Exception as e:
                    print(f"⚠️ Batch offline hash storage failed: {e}")

                results.append({
                    "file": file.filename,
                    "status": "success",
                    "protected_filename": output_filename,
                    "protected_file_data": protected_file_data,
                    "method": result.get('method', 'unknown'),
                    "original_hash": original_hash,
                    "protected_hash": protected_hash
                })
                successful += 1
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'Unsupported file type'
                results.append({"file": file.filename, "status": "failed", "error": error_msg})
                failed += 1
                
        finally:
            if temp_input and temp_input.exists():
                temp_input.unlink()
            if temp_output and temp_output.exists():
                temp_output.unlink()
    
    return BatchResponse(
        success=True,
        message=f"Batch processing completed. {successful} successful, {failed} failed.",
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )

@app.post("/batch-verify", response_model=BatchResponse)
async def batch_verify_documents(files: List[UploadFile] = File(...)):
    """
    Verify multiple documents in batch
    """
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        temp_file = None
        try:
            temp_file = TEMP_DIR / f"batch_verify_{uuid.uuid4()}_{file.filename}"
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            is_safe, reason = scan_file(str(temp_file))
            if not is_safe:
                results.append({"file": file.filename, "status": "failed", "error": f"File rejected: {reason}"})
                failed += 1
                continue
            
            ext = Path(file.filename).suffix.lower()
            
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                result = steg.extract_data_from_image(str(temp_file))
            elif ext == ".pdf":
                result = steg.extract_data_from_pdf(str(temp_file))
            elif ext in [".xlsx", ".xls", ".csv"]:
                result = steg.extract_data_from_excel(str(temp_file))
            else:
                result = None
            
            if result and result.get('success'):
                current_hash = hash_gen.generate_file_hash(str(temp_file))
                verification_result = offline_hash_manager.verify_document_offline(
                    filename=file.filename,
                    current_hash=current_hash
                )
                
                extracted_data = None
                if result.get('secret_data'):
                    is_valid, error_message = validate_extracted_data(result['secret_data'])
                    if is_valid:
                        extracted_data = result['secret_data'].decode('utf-8', errors='ignore')
                    else:
                        extracted_data = f"[SECURITY WARNING: Malicious content detected]"
                
                results.append({
                    "file": file.filename,
                    "status": "success",
                    "is_verified": verification_result['verified'],
                    "current_hash": current_hash,
                    "stored_hash": verification_result['stored_hash'] or "No hash found",
                    "extracted_data": extracted_data
                })
                successful += 1
            else:
                results.append({"file": file.filename, "status": "failed", "error": "Could not extract data or verify"})
                failed += 1
                
        finally:
            if temp_file and temp_file.exists():
                temp_file.unlink()
    
    return BatchResponse(
        success=True,
        message=f"Batch verification completed. {successful} successful, {failed} failed.",
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )

@app.get("/download/{file_id}")
async def download_protected_file(file_id: str):
    """
    This endpoint is deprecated. Downloads are handled via base64 data in the response.
    """
    raise HTTPException(status_code=410, detail="This endpoint is no longer available.")

@app.delete("/cleanup")
async def cleanup_temp_files_endpoint():
    """
    Clean up temporary files
    """
    try:
        cleanup_temp_files()
        return {"message": "Temporary files cleaned up successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate-path")
async def validate_path(path: str = Form(...)):
    """
    Validate a folder path for security and accessibility.
    """
    try:
        is_valid, message = validate_folder_path(path)
        
        if is_valid:
            sanitized_path = sanitize_path_for_display(path)
            return {
                "valid": True,
                "message": message,
                "sanitized_path": sanitized_path
            }
        else:
            return {
                "valid": False,
                "message": message,
                "sanitized_path": ""
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Path validation error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
