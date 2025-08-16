"""
DocProject API - Netlify Serverless Function
Converted from FastAPI to work as a Netlify serverless function
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
from multipart import MultipartParser

# Import all core business logic modules
from encryptor import DocumentEncryptor
from hash_generator import HashGenerator
from steganography import DocumentSteganography
from path_validator import validate_folder_path, sanitize_path
from security_validator import validate_secret_data, validate_extracted_data

# Global instances of the core modules
steganography = DocumentSteganography()
encryptor = DocumentEncryptor()
hash_gen = HashGenerator()

# --- Helper Functions ---
def get_cors_headers():
    """Returns standard CORS headers."""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }

def router(event, context):
    """Simple router to direct requests based on path."""
    path = event.get('path', '/')
    http_method = event.get('httpMethod', 'GET')

    if path == '/validate-path' and http_method == 'POST':
        return handle_validate_path(event, context)
    elif path == '/protect' and http_method == 'POST':
        return handle_protect_document(event, context)
    elif path == '/verify' and http_method == 'POST':
        return handle_verify_document(event, context)
    elif path == '/extract' and http_method == 'POST':
        return handle_extract_data(event, context)
    elif path == '/batch-protect' and http_method == 'POST':
        return handle_batch_protect(event, context)
    elif path == '/batch-verify' and http_method == 'POST':
        return handle_batch_verify(event, context)

    return {
        'statusCode': 404,
        'headers': get_cors_headers(),
        'body': json.dumps({'error': 'Not Found'})
    }

# --- Event Handlers ---

def handle_validate_path(event, context):
    """Handle path validation requests."""
    try:
        print(f"DEBUG: Raw event body type: {type(event.get('body'))}")
        print(f"DEBUG: Raw event body length: {len(event.get('body', ''))}")
        print(f"DEBUG: Is base64 encoded: {event.get('isBase64Encoded', False)}")
        
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')

        print(f"DEBUG: Decoded body: '{body}'")
        
        # Handle both FormData and JSON content
        content_type = event.get('headers', {}).get('content-type', '') or event.get('headers', {}).get('Content-Type', '')
        
        if 'multipart/form-data' in content_type:
            # Handle FormData from frontend
            parser = MultipartParser(body.encode() if isinstance(body, str) else body, content_type)
            form_data = parser.parse()
            path = form_data.fields.get('path', [b''])[0].decode('utf-8')
        elif 'application/x-www-form-urlencoded' in content_type:
            # Handle URL encoded form data
            data = parse_qs(body)
            path = data.get('path', [''])[0]
        else:
            # Handle JSON
            try:
                data = json.loads(body)
                path = data.get('path', '')
            except:
                # Fallback to form parsing
                data = parse_qs(body)
                path = data.get('path', [''])[0]

        # Debug: Log the received path
        print(f"DEBUG: Extracted path: '{path}'")
        print(f"DEBUG: Path type: {type(path)}")
        print(f"DEBUG: Path length: {len(path)}")
        print(f"DEBUG: Path repr: {repr(path)}")

        # Check if path is empty
        if not path or path.strip() == '':
            print(f"DEBUG: Path is empty or whitespace only")
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'valid': False,
                    'message': 'Path cannot be empty',
                    'sanitized_path': None
                })
            }

        # Use the actual validation functions from path_validator.py
        print(f"DEBUG: About to call validate_folder_path...")
        valid, message = validate_folder_path(path)
        print(f"DEBUG: validate_folder_path returned: valid={valid}, message='{message}'")
        
        sanitized_path = sanitize_path(path)
        print(f"DEBUG: sanitize_path returned: '{sanitized_path}'")

        response_data = {
            'valid': valid,
            'message': message,
            'sanitized_path': sanitized_path if valid else None
        }
        
        print(f"DEBUG: Final response data: {response_data}")

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(response_data)
        }
    except Exception as e:
        print(f"DEBUG: Exception in handle_validate_path: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Path validation error: {str(e)}'})
        }

def handle_protect_document(event, context):
    """Handles the protection of a single document."""
    try:
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body)

        parser = MultipartParser(body, event['headers']['Content-Type'])
        form_data = parser.parse()

        file_part = form_data.files.get('file')[0]
        secret_data_part = form_data.fields.get('secret_data')[0]
        output_folder_part = form_data.fields.get('output_folder')[0]
        encrypt_payload = form_data.fields.get('encrypt_payload')[0].lower() == 'true'
        password = form_data.fields.get('password', [''])[0]

        secret_data = secret_data_part.decode('utf-8')
        output_folder = output_folder_part.decode('utf-8')

        # Use the same path validation logic as in path_validator.py
        valid_path, path_message = validate_folder_path(output_folder)
        if not valid_path:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': path_message})
            }

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            original_hash = hash_gen.generate_file_hash(temp_file_path)

            if encrypt_payload:
                encrypted_result = encryptor.encrypt_data(secret_data.encode('utf-8'), password=password)
                if not encrypted_result['success']:
                    raise Exception(encrypted_result['message'])
                data_to_hide = encrypted_result['encrypted_data']
            else:
                data_to_hide = secret_data.encode('utf-8')

            output_path = os.path.join(output_folder, f"protected_{file_part.filename}")
            protection_result = steganography.hide_data(temp_file_path, data_to_hide, output_path, original_hash=original_hash, protected_hash=None)

            protected_hash = hash_gen.generate_file_hash(output_path)
            protection_result['protected_hash'] = protected_hash

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(protection_result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Document protection failed: {str(e)}'})
        }

def handle_verify_document(event, context):
    """Handles the verification of a single document."""
    try:
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body)

        parser = MultipartParser(body, event['headers']['Content-Type'])
        form_data = parser.parse()
        file_part = form_data.files.get('file')[0]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            extraction_result = steganography.extract_data(temp_file_path)
            if not extraction_result['success']:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps(extraction_result)
                }

            extracted_metadata = extraction_result['metadata']
            stored_protected_hash = extracted_metadata.get('protected_hash')

            current_hash = hash_gen.generate_file_hash(temp_file_path)
            is_verified = hash_gen.verify_hash(temp_file_path, stored_protected_hash)

            verification_result = {
                'file_name': file_part.filename,
                'status': 'success',
                'is_verified': is_verified,
                'current_hash': current_hash,
                'stored_hash': stored_protected_hash,
                'extracted_data': extracted_metadata.get('secret_data', '').decode('utf-8', 'ignore'),
                'extracted_original_hash': extracted_metadata.get('original_hash'),
                'extracted_method': extracted_metadata.get('method')
            }

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps(verification_result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Document verification failed: {str(e)}'})
        }

def handle_extract_data(event, context):
    """Handles extraction of data from a protected document."""
    try:
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body)

        parser = MultipartParser(body, event['headers']['Content-Type'])
        form_data = parser.parse()

        file_part = form_data.files.get('file')[0]
        password = form_data.fields.get('password', [''])[0]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_part.filename)
            with open(temp_file_path, 'wb') as f:
                f.write(file_part.content)

            extraction_result = steganography.extract_data(temp_file_path)

            if not extraction_result['success']:
                return {
                    'statusCode': 400,
                    'headers': get_cors_headers(),
                    'body': json.dumps(extraction_result)
                }

            extracted_metadata = extraction_result['metadata']
            extracted_secret = extracted_metadata.get('secret_data')

            if password and extracted_metadata.get('is_encrypted', False):
                decrypted_result = encryptor.decrypt_data(extracted_secret, password=password)
                if not decrypted_result['success']:
                    return {
                        'statusCode': 400,
                        'headers': get_cors_headers(),
                        'body': json.dumps(decrypted_result)
                    }
                final_secret_data = decrypted_result['decrypted_data'].decode('utf-8', 'ignore')
            else:
                final_secret_data = extracted_secret.decode('utf-8', 'ignore')

            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'file_name': file_part.filename,
                    'status': 'success',
                    'extracted_data': final_secret_data,
                    'metadata': {
                        'original_hash': extracted_metadata.get('original_hash'),
                        'protected_hash': extracted_metadata.get('protected_hash')
                    }
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Data extraction failed: {str(e)}'})
        }

def handle_batch_protect(event, context):
    """Handles batch protection for multiple documents."""
    try:
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body)

        parser = MultipartParser(body, event['headers']['Content-Type'])
        form_data = parser.parse()

        files = form_data.files.get('file', [])
        secret_data_part = form_data.fields.get('secret_data', [''])[0]
        output_folder_part = form_data.fields.get('output_folder', [''])[0]
        encrypt_payload = form_data.fields.get('encrypt_payload', ['false'])[0].lower() == 'true'
        password = form_data.fields.get('password', [''])[0]

        secret_data = secret_data_part.decode('utf-8')
        output_folder = output_folder_part.decode('utf-8')

        # Use the same path validation logic as in path_validator.py
        valid_path, path_message = validate_folder_path(output_folder)
        if not valid_path:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': path_message})
            }

        if not files:
            raise ValueError("No files provided for batch protection.")

        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file_part in files:
                try:
                    temp_file_path = os.path.join(temp_dir, file_part.filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_part.content)

                    original_hash = hash_gen.generate_file_hash(temp_file_path)

                    if encrypt_payload:
                        encrypted_result = encryptor.encrypt_data(secret_data.encode('utf-8'), password=password)
                        if not encrypted_result['success']:
                            raise Exception(encrypted_result['message'])
                        data_to_hide = encrypted_result['encrypted_data']
                    else:
                        data_to_hide = secret_data.encode('utf-8')

                    protected_file_path = os.path.join(output_folder, f"protected_{file_part.filename}")
                    protection_result = steganography.hide_data(temp_file_path, data_to_hide, protected_file_path, original_hash=original_hash)

                    if protection_result['success']:
                        protected_hash = hash_gen.generate_file_hash(protected_file_path)
                        protection_result['protected_hash'] = protected_hash

                    results.append({
                        'file_name': file_part.filename,
                        'status': 'success',
                        'result': protection_result
                    })
                except Exception as e:
                    results.append({
                        'file_name': file_part.filename,
                        'status': 'error',
                        'error': f'Protection failed: {str(e)}'
                    })

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'batch_results': results})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Batch protection failed: {str(e)}'})
        }

def handle_batch_verify(event, context):
    """Handles batch verification for multiple documents."""
    try:
        body = event.get('body', '')
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body)

        parser = MultipartParser(body, event['headers']['Content-Type'])
        form_data = parser.parse()

        files = form_data.files.get('file', [])

        if not files:
            raise ValueError("No files provided for batch verification.")

        results = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for file_part in files:
                try:
                    temp_file_path = os.path.join(temp_dir, file_part.filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(file_part.content)

                    extraction_result = steganography.extract_data(temp_file_path)

                    if not extraction_result['success']:
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
                        'method': extracted_metadata.get('method')
                    }
                    results.append(verification_data)

                except Exception as e:
                    results.append({
                        'file_name': file_part.filename,
                        'status': 'error',
                        'error': f'Verification failed: {str(e)}'
                    })

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({'batch_results': results})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Batch verification failed: {str(e)}'})
        }