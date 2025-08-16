"""
DocProject API - Netlify Serverless Function (FIXED VERSION)
Enhanced error handling and proper JSON responses
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

# Import all core business logic modules with error handling
try:
    from encryptor import DocumentEncryptor
    from hash_generator import HashGenerator
    from steganography import DocumentSteganography
    from path_validator import validate_folder_path, sanitize_path
    from security_validator import validate_secret_data, validate_extracted_data
    
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
    
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps(data)
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
        print(f"DEBUG: Body type: {type(body)}, length: {len(str(body))}")

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
        print(f"DEBUG: Received event: {json.dumps(event, default=str)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({'message': 'CORS preflight successful'})
            }

        # Check if modules are loaded
        if not MODULES_LOADED:
            return create_error_response(500, "Server modules not properly loaded")

        # Extract path and method
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        
        print(f"DEBUG: Processing {http_method} {path}")

        # Route requests
        if path.endswith('/validate-path') and http_method == 'POST':
            return handle_validate_path(event, context)
        elif path.endswith('/protect') and http_method == 'POST':
            return handle_protect_document(event, context)
        elif path.endswith('/verify') and http_method == 'POST':
            return handle_verify_document(event, context)
        elif path.endswith('/extract') and http_method == 'POST':
            return handle_extract_data(event, context)
        elif path.endswith('/batch-protect') and http_method == 'POST':
            return handle_batch_protect(event, context)
        elif path.endswith('/batch-verify') and http_method == 'POST':
            return handle_batch_verify(event, context)
        else:
            return create_error_response(404, f"Endpoint not found: {http_method} {path}")

    except Exception as e:
        print(f"ERROR in handler: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Internal server error: {str(e)}")

def handle_validate_path(event, context):
    """Handle path validation requests with enhanced error handling."""
    try:
        print("DEBUG: Starting path validation")
        
        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        # Extract path from form data
        path_field = form_data.fields.get('path', [b''])
        if not path_field:
            return create_success_response({
                'valid': False,
                'message': 'Path field not found in request',
                'sanitized_path': None
            })

        path = path_field[0].decode('utf-8') if isinstance(path_field[0], bytes) else str(path_field[0])
        path = path.strip()

        print(f"DEBUG: Validating path: '{path}'")

        # Check if path is empty
        if not path:
            return create_success_response({
                'valid': False,
                'message': 'Path cannot be empty',
                'sanitized_path': None
            })

        # Use validation functions
        try:
            valid, message = validate_folder_path(path)
            sanitized_path = sanitize_path(path)
        except Exception as validation_error:
            print(f"DEBUG: Validation function error: {validation_error}")
            return create_success_response({
                'valid': False,
                'message': f'Path validation failed: {str(validation_error)}',
                'sanitized_path': None
            })

        response_data = {
            'valid': valid,
            'message': message or ('Path is valid' if valid else 'Path is invalid'),
            'sanitized_path': sanitized_path if valid else None
        }

        print(f"DEBUG: Validation result: {response_data}")
        return create_success_response(response_data)

    except Exception as e:
        print(f"ERROR in handle_validate_path: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Path validation error: {str(e)}")

def handle_protect_document(event, context):
    """Handle document protection with enhanced error handling."""
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
        encrypt_payload = form_data.fields.get('encrypt_payload', [b'false'])[0]
        password = form_data.fields.get('password', [b''])[0]

        # Decode form data
        secret_data = secret_data_part.decode('utf-8') if isinstance(secret_data_part, bytes) else str(secret_data_part)
        output_folder = output_folder_part.decode('utf-8') if isinstance(output_folder_part, bytes) else str(output_folder_part)
        encrypt_payload = str(encrypt_payload).lower() in ('true', '1', 'yes')
        password = password.decode('utf-8') if isinstance(password, bytes) else str(password)

        print(f"DEBUG: Processing file: {file_part.filename}")
        print(f"DEBUG: Encrypt payload: {encrypt_payload}")

        # Process the document
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            output_path = os.path.join(temp_dir, f"protected_{file_part.filename}")
            
            # Write uploaded file
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            # Generate original hash
            original_hash = hash_gen.generate_file_hash(temp_file_path)

            # Prepare data to hide
            if encrypt_payload and password:
                encrypted_result = encryptor.encrypt_data(secret_data.encode('utf-8'), password=password)
                if not encrypted_result['success']:
                    return create_error_response(400, f"Encryption failed: {encrypted_result['message']}")
                data_to_hide = encrypted_result['encrypted_data']
            else:
                data_to_hide = secret_data.encode('utf-8')

            # Protect the document
            protection_result = steganography.hide_data(
                temp_file_path, 
                data_to_hide, 
                output_path, 
                original_hash=original_hash
            )

            if not protection_result.get('success'):
                return create_error_response(400, f"Protection failed: {protection_result.get('message', 'Unknown error')}")

            # Generate protected hash
            if os.path.exists(output_path):
                # Read the protected file for download
                with open(output_path, 'rb') as f_protected:
                    protected_file_data = f_protected.read()
                
                protected_hash = hash_gen.generate_file_hash(output_path)
                protection_result['protected_hash'] = protected_hash
                
                # Add file data for download
                protection_result['file_data'] = base64.b64encode(protected_file_data).decode('utf-8')
                protection_result['file_name'] = os.path.basename(output_path)
            
            protection_result['file_name'] = file_part.filename
            
        return create_success_response(protection_result)

    except Exception as e:
        print(f"ERROR in handle_protect_document: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Document protection failed: {str(e)}")

def handle_verify_document(event, context):
    """Handle document verification with enhanced error handling."""
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
            
            # Write uploaded file
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            # Extract data from document
            extraction_result = steganography.extract_data(temp_file_path)
            if not extraction_result.get('success'):
                return create_error_response(400, f"Data extraction failed: {extraction_result.get('error', 'Unknown error')}")

            extracted_metadata = extraction_result['metadata']
            stored_protected_hash = extracted_metadata.get('protected_hash')

            # Generate current hash and verify
            current_hash = hash_gen.generate_file_hash(temp_file_path)
            is_verified = False
            
            if stored_protected_hash:
                is_verified = hash_gen.verify_hash(temp_file_path, stored_protected_hash)
            
            verification_result = {
                'file_name': file_part.filename,
                'is_verified': is_verified,
                'current_hash': current_hash,
                'stored_hash': stored_protected_hash,
                'extracted_data': extracted_metadata.get('secret_data', b'').decode('utf-8', 'ignore'),
                'extracted_original_hash': extracted_metadata.get('original_hash'),
                'method': extracted_metadata.get('method', 'unknown')
            }

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
        password = form_data.fields.get('password', [b''])[0]
        password = password.decode('utf-8') if isinstance(password, bytes) else str(password)

        print(f"DEBUG: Extracting from file: {file_part.filename}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            
            # Write uploaded file
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            # Extract data
            extraction_result = steganography.extract_data(temp_file_path)
            if not extraction_result.get('success'):
                return create_error_response(400, f"Extraction failed: {extraction_result.get('error', 'Unknown error')}")

            extracted_metadata = extraction_result['metadata']
            extracted_secret = extracted_metadata.get('secret_data', b'')

            # Decrypt if password provided and data is encrypted
            if password and extracted_metadata.get('is_encrypted', False):
                decrypted_result = encryptor.decrypt_data(extracted_secret, password=password)
                if not decrypted_result.get('success'):
                    return create_error_response(400, f"Decryption failed: {decrypted_result.get('message', 'Invalid password')}")
                final_secret_data = decrypted_result['decrypted_data'].decode('utf-8', 'ignore')
            else:
                final_secret_data = extracted_secret.decode('utf-8', 'ignore')

            result = {
                'file_name': file_part.filename,
                'extracted_data': final_secret_data,
                'metadata': {
                    'original_hash': extracted_metadata.get('original_hash'),
                    'protected_hash': extracted_metadata.get('protected_hash'),
                    'method': extracted_metadata.get('method', 'unknown'),
                    'is_encrypted': extracted_metadata.get('is_encrypted', False)
                }
            }

        return create_success_response(result)

    except Exception as e:
        print(f"ERROR in handle_extract_data: {e}")
        traceback.print_exc()
        return create_error_response(500, f"Data extraction failed: {str(e)}")

def handle_batch_protect(event, context):
    """Handle batch protection with enhanced error handling."""
    try:
        print("DEBUG: Starting batch protection")
        
        form_data, error = parse_form_data(event)
        if error:
            return create_error_response(400, f"Form parsing error: {error}")

        files = form_data.files.get('file', [])
        if not files:
            return create_error_response(400, "No files provided for batch protection")

        # Extract common parameters
        secret_data_part = form_data.fields.get('secret_data', [b''])[0]
        encrypt_payload = form_data.fields.get('encrypt_payload', [b'false'])[0]
        password = form_data.fields.get('password', [b''])[0]

        secret_data = secret_data_part.decode('utf-8') if isinstance(secret_data_part, bytes) else str(secret_data_part)
        encrypt_payload = str(encrypt_payload).lower() in ('true', '1', 'yes')
        password = password.decode('utf-8') if isinstance(password, bytes) else str(password)

        # Process all files
        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file_part in files:
                try:
                    print(f"DEBUG: Processing file: {file_part.filename}")
                    
                    temp_file_path = os.path.join(temp_dir, file_part.filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_part.content)

                    original_hash = hash_gen.generate_file_hash(temp_file_path)

                    # Prepare data to hide
                    if encrypt_payload and password:
                        encrypted_result = encryptor.encrypt_data(secret_data.encode('utf-8'), password=password)
                        if not encrypted_result['success']:
                            raise Exception(f"Encryption failed: {encrypted_result['message']}")
                        data_to_hide = encrypted_result['encrypted_data']
                    else:
                        data_to_hide = secret_data.encode('utf-8')

                    # Protect document
                    protected_file_path = os.path.join(temp_dir, f"protected_{file_part.filename}")
                    protection_result = steganography.hide_data(
                        temp_file_path, 
                        data_to_hide, 
                        protected_file_path, 
                        original_hash=original_hash
                    )

                    if protection_result.get('success'):
                        if os.path.exists(protected_file_path):
                            with open(protected_file_path, 'rb') as f_protected:
                                protected_file_data = f_protected.read()

                            protected_hash = hash_gen.generate_file_hash(protected_file_path)
                            protection_result['protected_hash'] = protected_hash
                            
                            protection_result['file_data'] = base64.b64encode(protected_file_data).decode('utf-8')
                            protection_result['file_name'] = os.path.basename(protected_file_path)
                            
                    results.append({
                        'file_name': file_part.filename,
                        'status': 'success',
                        'result': protection_result
                    })

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
    """Handle batch verification with enhanced error handling."""
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
                    print(f"DEBUG: Verifying file: {file_part.filename}")
                    
                    temp_file_path = os.path.join(temp_dir, file_part.filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_part.content)

                    # Extract and verify
                    extraction_result = steganography.extract_data(temp_file_path)

                    if not extraction_result.get('success'):
                        results.append({
                            'file_name': file_part.filename,
                            'status': 'error',
                            'error': extraction_result.get('error', 'Unknown extraction error')
                        })
                        continue

                    extracted_metadata = extraction_result['metadata']
                    stored_protected_hash = extracted_metadata.get('protected_hash')
                    current_hash = hash_gen.generate_file_hash(temp_file_path)

                    is_verified = False
                    if stored_protected_hash and current_hash:
                        is_verified = stored_protected_hash.lower() == current_hash.lower()

                    verification_data = {
                        'file_name': file_part.filename,
                        'status': 'success',
                        'verification_status': 'verified' if is_verified else 'tampered',
                        'is_verified': is_verified,
                        'current_hash': current_hash,
                        'stored_hash': stored_protected_hash,
                        'extracted_data': extracted_metadata.get('secret_data', b'').decode('utf-8', 'ignore'),
                        'method': extracted_metadata.get('method', 'unknown')
                    }
                    results.append(verification_data)

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
# If you're using a different serverless platform, adjust accordingly