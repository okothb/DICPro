"""
DocProject API - Netlify Serverless Function (FIXED VERSION)
Enhanced error handling and proper JSON responses
*** MODIFIED TO USE UPSTASH REDIS INSTEAD OF SQL DATABASE ***
"""

import json
import os
import tempfile
import shutil
import base64
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from urllib.parse import parse_qs
import traceback

try:
    from multipart import MultipartParser
except ImportError:
    # Fallback parser if multipart is not available
    class MultipartParser:
        def __init__(self, data, content_type):
            self.data = data
            self.content_type = content_type
        def parse(self):
            return type('obj', (object,), {'files': {}, 'fields': {}})

try:
    from upstash_redis import Redis
except ImportError:
    Redis = None

# Import all core business logic modules with error handling (use core package)
try:
    from core.encryptor import DocumentEncryptor
    from core.hash_generator import HashGenerator
    from core.steganography import DocumentSteganography
    from core.path_validator import validate_folder_path, sanitize_path
    from core.security_validator import validate_secret_data, validate_extracted_data

    # --- NEW: Initialize Upstash Redis Client ---
    redis_client = None
    REDIS_LOADED = False
    if Redis:
        try:
            redis_url = os.environ.get("UPSTASH_REDIS_REST_URL")
            redis_token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

            if not redis_url or not redis_token:
                raise ValueError("UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN environment variables must be set.")

            redis_client = Redis(url=redis_url, token=redis_token)
            redis_client.ping() # Check connection on startup
            print("Successfully connected to Upstash Redis.")
            REDIS_LOADED = True
        except Exception as e:
            print(f"CRITICAL: Failed to initialize Upstash Redis: {e}")
            REDIS_LOADED = False
    # --- END NEW ---

    # Global instances of the core modules
    steganography = DocumentSteganography()
    encryptor = DocumentEncryptor()
    hash_gen = HashGenerator()
    MODULES_LOADED = True

except ImportError as e:
    print(f"WARNING: Failed to import modules: {e}")
    MODULES_LOADED = False

def get_cors_headers():
    """Returns standard CORS headers."""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }

def create_error_response(status_code, error_message, additional_info=None):
    """Create a standardized error response."""
    response_body = {
        'error': str(error_message),
        'success': False,
        'status_code': status_code
    }
    if additional_info:
        response_body.update(additional_info)

    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(response_body)
    }

def create_success_response(data, status_code=200):
    """Create a standardized success response."""
    if not isinstance(data, dict):
        data = {'result': data}

    data['success'] = True

    # Custom JSON serializer to handle datetime objects
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(data, default=json_serializer)
    }

def safe_json_loads(data):
    """Safely parse JSON with error handling."""
    try:
        return json.loads(data), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return None, f"JSON parsing error: {str(e)}"

def parse_form_data(event):
    """Parse form data with enhanced error handling."""
    try:
        body = event.get('body', '')
        if not body:
            return None, "Request body is empty"

        # Handle base64 encoded body
        if event.get('isBase64Encoded'):
            try:
                body = base64.b64decode(body)
            except Exception as e:
                return None, f"Base64 decode error: {str(e)}"

        # Get content type
        headers = event.get('headers', {})
        content_type = (headers.get('content-type') or
                       headers.get('Content-Type') or
                       headers.get('Content-type', ''))

        print(f"DEBUG: Content-Type: {content_type}")
        # print(f"DEBUG: Body type: {type(body)}, length: {len(str(body))}") # Avoid printing large bodies

        # Parse based on content type
        if 'multipart/form-data' in content_type:
            if isinstance(body, str):
                body = body.encode('utf-8')
            parser = MultipartParser(body, content_type)
            return parser.parse(), None
        elif 'application/json' in content_type:
            body_str = body.decode('utf-8') if isinstance(body, bytes) else str(body)
            data, error = safe_json_loads(body_str)
            if error:
                return None, error
            # Convert JSON to form-like structure
            form_like = type('obj', (object,), {
                'fields': {k: [str(v).encode('utf-8')] for k, v in data.items()},
                'files': {}
            })
            return form_like, None
        elif 'application/x-www-form-urlencoded' in content_type:
            body_str = body.decode('utf-8') if isinstance(body, bytes) else str(body)
            parsed = parse_qs(body_str)
            form_like = type('obj', (object,), {
                'fields': {k: [v[0].encode('utf-8')] for k, v in parsed.items()},
                'files': {}
            })
            return form_like, None
        else:
            return None, f"Unsupported content type: {content_type}"

    except Exception as e:
        print(f"ERROR in parse_form_data: {e}")
        traceback.print_exc()
        return None, f"Form parsing error: {str(e)}"

def handler(event, context):
    """Main Netlify function handler with comprehensive error handling."""
    try:
        # print(f"DEBUG: Received event: {json.dumps(event, default=str)}")

        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({'message': 'CORS preflight successful'})
            }

        # Check if modules are loaded
        if not MODULES_LOADED:
            return create_error_response(500, "Server core modules not properly loaded")
        # NEW: Check if Redis is connected
        if not REDIS_LOADED:
            return create_error_response(500, "Server database (Redis) connection failed. Check configuration.")


        # Extract path and method
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')

        print(f"DEBUG: Processing {http_method} {path}")

        # Route requests
        if path.endswith('/protect') and http_method == 'POST':
            return handle_protect_document(event, context)
        elif path.endswith('/verify') and http_method == 'POST':
            return handle_verify_document(event, context)
        elif path.endswith('/extract') and http_method == 'POST':
            return handle_extract_data(event, context)
        elif path.endswith('/batch-protect') and http_method == 'POST':
            return handle_batch_protect(event, context)
        elif path.endswith('/batch-verify') and http_method == 'POST':
            return handle_batch_verify(event, context)
        elif path.endswith('/health') and http_method in ('GET', 'POST'):
            # Basic health check including DB connectivity
            db_ok = False
            try:
                # NEW: Ping Redis to check connectivity
                redis_client.ping()
                db_ok = True
            except Exception as e:
                print(f"Health check Redis ping failed: {e}")
                db_ok = False
            return create_success_response({
                'service': 'DocProject Netlify API',
                'time': datetime.now().isoformat(),
                'db_connected': db_ok
            })
        else:
            return create_error_response(404, f"Endpoint not found: {http_method} {path}")

    except Exception as e:
        print(f"ERROR in handler: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Internal server error: {str(e)}")

def _wrap_secret_data(secret_text: str, encrypt: bool, password: str, enc: DocumentEncryptor) -> bytes:
    """Prepare bytes to embed. If encrypt=True, wrap encrypted payload JSON."""
    if encrypt and password:
        enc_result = enc.encrypt_string(secret_text, password)
        if not enc_result.get('success'):
            raise ValueError(enc_result.get('error', 'Encryption failed'))
        return json.dumps({'encrypted': True, 'payload': enc_result}).encode('utf-8')
    return secret_text.encode('utf-8')

def _unwrap_secret_data(secret_bytes: bytes, password: Optional[str], enc: DocumentEncryptor) -> str:
    """Extract string from embedded bytes, decrypting if wrapped JSON."""
    try:
        text = secret_bytes.decode('utf-8', 'ignore')
    except Exception:
        return ""
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and obj.get('encrypted') and isinstance(obj.get('payload'), dict):
            if not password:
                return 'Data is encrypted. Password required for extraction.'
            decrypted = enc.decrypt_string(obj['payload'], password)
            return decrypted if decrypted is not None else 'Decryption failed: Invalid password or data.'
    except Exception:
        pass
    return text

def handle_protect_document(event, context):
    """Handle document protection with Redis integration."""
    try:
        print("DEBUG: Starting document protection")

        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        # Extract form fields
        file_list = form_data.files.get('file', [])
        if not file_list:
            return create_error_response(400, "No file provided")

        file_part = file_list[0]
        secret_data_part = form_data.fields.get('secret_data', [b''])[0]
        encrypt_payload_part = form_data.fields.get('encrypt_payload', [b'false'])[0]
        password_part = form_data.fields.get('password', [b''])[0]

        # Decode form data
        secret_data = secret_data_part.decode('utf-8')
        encrypt_payload = encrypt_payload_part.decode('utf-8').lower() in ('true', '1', 'yes')
        password = password_part.decode('utf-8')

        print(f"DEBUG: Processing file: {file_part.filename}")
        print(f"DEBUG: Encrypt payload: {encrypt_payload}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            output_path = os.path.join(temp_dir, f"protected_{file_part.filename}")

            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            original_hash = hash_gen.generate_file_hash(temp_file_path)

            # Prepare payload (optionally encrypted)
            data_to_hide = _wrap_secret_data(secret_data, encrypt_payload, password, encryptor)

            # Determine file type and protect accordingly
            ext = Path(file_part.filename).suffix.lower()
            protected_path = output_path
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                result = steganography.hide_data_in_image(
                    temp_file_path, data_to_hide, output_path, original_hash=original_hash
                )
                if not result.get('success'):
                    return create_error_response(400, f"Protection failed: {result.get('error', 'Unknown error')}")
                protected_path = result.get('stego_image', output_path)
            elif ext == ".pdf":
                result = steganography.hide_data_in_pdf(
                    temp_file_path, data_to_hide, output_path, original_hash=original_hash
                )
                if not result.get('success'):
                    return create_error_response(400, f"Protection failed: {result.get('error', 'Unknown error')}")
                protected_path = result.get('stego_document', output_path)
            elif ext in [".xlsx", ".xls", ".csv"]:
                result = steganography.hide_data_in_excel(
                    temp_file_path, data_to_hide, output_path, original_hash=original_hash
                )
                if not result.get('success'):
                    return create_error_response(400, f"Protection failed: {result.get('error', 'Unknown error')}")
                protected_path = result.get('stego_excel', output_path)
            elif ext == ".docx":
                result = steganography.hide_data_in_docx(
                    temp_file_path, data_to_hide, output_path, original_hash=original_hash
                )
                if not result.get('success'):
                    return create_error_response(400, f"Protection failed: {result.get('error', 'Unknown error')}")
                protected_path = result.get('stego_document', output_path)
            else:
                return create_error_response(400, f"Unsupported file type: {ext}")

            if os.path.exists(protected_path):
                with open(protected_path, 'rb') as f_protected:
                    protected_file_data = f_protected.read()

                protected_hash = hash_gen.generate_file_hash(protected_path)

                # *** NEW: Store hashes in Upstash Redis ***
                if original_hash and protected_hash:
                    record_data = {
                        "original_hash": original_hash,
                        "original_filename": file_part.filename,
                        "created_at": datetime.now().isoformat()
                    }
                    redis_client.set(protected_hash, json.dumps(record_data))
                    print(f"DEBUG: Stored record for {file_part.filename} in Redis.")


                result['protected_hash'] = protected_hash
                result['file_data'] = base64.b64encode(protected_file_data).decode('utf-8')
                result['file_name'] = os.path.basename(protected_path)

            result['original_hash'] = original_hash

        return create_success_response(result)

    except Exception as e:
        print(f"ERROR in handle_protect_document: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Document protection failed: {str(e)}")

def handle_verify_document(event, context):
    """Handle document verification against Redis."""
    try:
        print("DEBUG: Starting document verification")

        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        file_list = form_data.files.get('file', [])
        if not file_list:
            return create_error_response(400, "No file provided for verification")

        file_part = file_list[0]
        print(f"DEBUG: Verifying file: {file_part.filename}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            current_hash = hash_gen.generate_file_hash(temp_file_path)

            # *** NEW: Verify hash against Upstash Redis ***
            db_record_json = redis_client.get(current_hash)
            db_record = json.loads(db_record_json) if db_record_json else None

            is_verified = db_record is not None

            verification_result = {
                'file_name': file_part.filename,
                'is_verified': is_verified,
                'current_hash': current_hash,
                'message': 'Document is authentic and verified.' if is_verified else 'Document is not recognized or has been tampered with.'
            }

            if is_verified:
                verification_result.update({
                    'original_hash': db_record.get('original_hash'),
                    'original_filename': db_record.get('original_filename'),
                    'protection_date': db_record.get('created_at')
                })

        return create_success_response(verification_result)

    except Exception as e:
        print(f"ERROR in handle_verify_document: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Document verification failed: {str(e)}")


def handle_extract_data(event, context):
    """Handle data extraction with enhanced error handling."""
    try:
        print("DEBUG: Starting data extraction")

        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        file_list = form_data.files.get('file', [])
        if not file_list:
            return create_error_response(400, "No file provided for extraction")

        file_part = file_list[0]
        password_part = form_data.fields.get('password', [b''])[0]
        password = password_part.decode('utf-8')

        print(f"DEBUG: Extracting from file: {file_part.filename}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)

            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            # Determine file type and extract accordingly
            ext = Path(file_part.filename).suffix.lower()
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                extraction_result = steganography.extract_data_from_image(temp_file_path)
            elif ext == ".pdf":
                extraction_result = steganography.extract_data_from_pdf(temp_file_path)
            elif ext in [".xlsx", ".xls", ".csv"]:
                extraction_result = steganography.extract_data_from_excel(temp_file_path)
            elif ext == ".docx":
                extraction_result = steganography.extract_data_from_docx(temp_file_path)
            else:
                return create_error_response(400, f"Unsupported file type: {ext}")

            if not extraction_result.get('success'):
                return create_error_response(400, f"Extraction failed: {extraction_result.get('error', 'Unknown error')}")

            extracted_metadata = extraction_result.get('metadata', {})
            extracted_secret = extraction_result.get('secret_data', b'')

            if extracted_secret:
                final_secret_data = _unwrap_secret_data(extracted_secret, password, encryptor)
            else:
                final_secret_data = "No secret data found in the document."

            result = {
                'file_name': file_part.filename,
                'extracted_data': final_secret_data,
                'metadata': {
                    'original_hash': extracted_metadata.get('original_hash'),
                    'method': extracted_metadata.get('method', 'unknown'),
                }
            }

        return create_success_response(result)

    except Exception as e:
        print(f"ERROR in handle_extract_data: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Data extraction failed: {str(e)}")

def handle_batch_protect(event, context):
    """Handle batch protection with Redis integration."""
    try:
        print("DEBUG: Starting batch protection")

        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        files = form_data.files.get('file', [])
        if not files:
            return create_error_response(400, "No files provided for batch protection")

        secret_data_part = form_data.fields.get('secret_data', [b''])[0]
        encrypt_payload_part = form_data.fields.get('encrypt_payload', [b'false'])[0]
        password_part = form_data.fields.get('password', [b''])[0]

        secret_data = secret_data_part.decode('utf-8')
        encrypt_payload = encrypt_payload_part.decode('utf-8').lower() in ('true', '1', 'yes')
        password = password_part.decode('utf-8')

        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file_part in files:
                try:
                    print(f"DEBUG: Batch processing file: {file_part.filename}")

                    temp_file_path = os.path.join(temp_dir, file_part.filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_part.content)

                    original_hash = hash_gen.generate_file_hash(temp_file_path)

                    # Prepare payload (optionally encrypted)
                    data_to_hide = _wrap_secret_data(secret_data, encrypt_payload, password, encryptor)

                    protected_file_path = os.path.join(temp_dir, f"protected_{file_part.filename}")

                    ext = Path(file_part.filename).suffix.lower()
                    if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                        protection_result = steganography.hide_data_in_image(
                            temp_file_path, data_to_hide, protected_file_path, original_hash=original_hash
                        )
                        success = protection_result.get('success')
                        final_path = protection_result.get('stego_image', protected_file_path)
                    elif ext == ".pdf":
                        protection_result = steganography.hide_data_in_pdf(
                            temp_file_path, data_to_hide, protected_file_path, original_hash=original_hash
                        )
                        success = protection_result.get('success')
                        final_path = protection_result.get('stego_document', protected_file_path)
                    elif ext in [".xlsx", ".xls", ".csv"]:
                        protection_result = steganography.hide_data_in_excel(
                            temp_file_path, data_to_hide, protected_file_path, original_hash=original_hash
                        )
                        success = protection_result.get('success')
                        final_path = protection_result.get('stego_excel', protected_file_path)
                    elif ext == ".docx":
                        protection_result = steganography.hide_data_in_docx(
                            temp_file_path, data_to_hide, protected_file_path, original_hash=original_hash
                        )
                        success = protection_result.get('success')
                        final_path = protection_result.get('stego_document', protected_file_path)
                    else:
                        raise Exception(f"Unsupported file type: {ext}")

                    if success:
                        with open(final_path, 'rb') as f_protected:
                            protected_file_data = f_protected.read()

                        protected_hash = hash_gen.generate_file_hash(final_path)

                        # *** NEW: Store hashes in Redis for each file ***
                        if original_hash and protected_hash:
                            record_data = {
                                "original_hash": original_hash,
                                "original_filename": file_part.filename,
                                "created_at": datetime.now().isoformat()
                            }
                            redis_client.set(protected_hash, json.dumps(record_data))

                        results.append({
                            'file_name': file_part.filename,
                            'status': 'success',
                            'result': {
                                'success': True,
                                'protected_hash': protected_hash,
                                'file_data': base64.b64encode(protected_file_data).decode('utf-8'),
                                'file_name': os.path.basename(final_path)
                            }
                        })
                    else:
                        raise Exception(protection_result.get('error', protection_result.get('message', 'Unknown protection error')))

                except Exception as file_error:
                    print(f"ERROR processing {file_part.filename}: {file_error}")
                    results.append({
                        'file_name': file_part.filename,
                        'status': 'error',
                        'error': str(file_error)
                    })

        return create_success_response({'batch_results': results})

    except Exception as e:
        print(f"ERROR in handle_batch_protect: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Batch protection failed: {str(e)}")

def handle_batch_verify(event, context):
    """Handle batch verification against Redis."""
    try:
        print("DEBUG: Starting batch verification")

        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        files = form_data.files.get('file', [])
        if not files:
            return create_error_response(400, "No files provided for batch verification")

        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file_part in files:
                try:
                    print(f"DEBUG: Batch verifying file: {file_part.filename}")

                    temp_file_path = os.path.join(temp_dir, file_part.filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_part.content)

                    current_hash = hash_gen.generate_file_hash(temp_file_path)

                    # *** NEW: Verify each file against Redis ***
                    db_record = redis_client.get(current_hash) # Just check for existence

                    is_verified = db_record is not None

                    results.append({
                        'file_name': file_part.filename,
                        'status': 'success',
                        'is_verified': is_verified,
                        'verification_status': 'verified' if is_verified else 'tampered',
                        'current_hash': current_hash,
                    })

                except Exception as file_error:
                    print(f"ERROR verifying {file_part.filename}: {file_error}")
                    results.append({
                        'file_name': file_part.filename,
                        'status': 'error',
                        'error': str(file_error)
                    })

        return create_success_response({'batch_results': results})

    except Exception as e:
        print(f"ERROR in handle_batch_verify: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Batch verification failed: {str(e)}")

# For Netlify, the function should be named 'handler'