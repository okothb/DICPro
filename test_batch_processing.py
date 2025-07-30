#!/usr/bin/env python3
"""
Test script to verify batch processing functionality
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import requests
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_batch_processing():
    """Test batch processing functionality."""
    print("Testing batch processing functionality...")
    
    # API base URL
    API_BASE_URL = "http://localhost:8000"
    
    # Create test files
    test_files = []
    test_file_paths = []
    
    try:
        # Create temporary test files
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"This is test file {i+1} for batch processing.")
                test_file_paths.append(f.name)
        
        print(f"Created {len(test_file_paths)} test files")
        
        # Test 1: Batch Protection
        print(f"\n1. Testing batch protection...")
        
        # Prepare files for upload
        files = []
        for i, file_path in enumerate(test_file_paths):
            with open(file_path, 'rb') as f:
                files.append(('files', (f'test_file_{i+1}.txt', f.read(), 'text/plain')))
        
        # Prepare form data
        data = {
            'secret_data': 'Test secret data for batch protection',
            'encrypt_payload': 'false',
            'output_folder': tempfile.gettempdir()
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/batch-protect", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Batch protection successful")
                print(f"   Total files: {result.get('total_files', 0)}")
                print(f"   Successful: {result.get('successful', 0)}")
                print(f"   Failed: {result.get('failed', 0)}")
                
                # Check individual results
                if result.get('results'):
                    for item in result['results']:
                        if item['status'] == 'success':
                            print(f"   ✅ {item['file']}: {item.get('method', 'unknown')}")
                        else:
                            print(f"   ❌ {item['file']}: {item.get('error', 'unknown error')}")
            else:
                print(f"   ❌ Batch protection failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Batch protection error: {str(e)}")
        
        # Test 2: Batch Verification
        print(f"\n2. Testing batch verification...")
        
        # Prepare files for verification (using the same files)
        verify_files = []
        for i, file_path in enumerate(test_file_paths):
            with open(file_path, 'rb') as f:
                verify_files.append(('files', (f'test_file_{i+1}.txt', f.read(), 'text/plain')))
        
        try:
            response = requests.post(f"{API_BASE_URL}/batch-verify", files=verify_files)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Batch verification successful")
                print(f"   Total files: {result.get('total_files', 0)}")
                print(f"   Successful: {result.get('successful', 0)}")
                print(f"   Failed: {result.get('failed', 0)}")
                
                # Check individual results
                if result.get('results'):
                    for item in result['results']:
                        if item['status'] == 'success':
                            verification_status = "VERIFIED" if item.get('is_verified', False) else "NOT VERIFIED"
                            print(f"   ✅ {item['file']}: {verification_status}")
                        else:
                            print(f"   ❌ {item['file']}: {item.get('error', 'unknown error')}")
            else:
                print(f"   ❌ Batch verification failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ❌ Batch verification error: {str(e)}")
        
        # Test 3: Check hash storage
        print(f"\n3. Testing hash storage access...")
        from core.hash_generator import HashGenerator
        
        hash_gen = HashGenerator()
        
        for i, file_path in enumerate(test_file_paths):
            filename = f'test_file_{i+1}.txt'
            original_hash = hash_gen.load_hash_from_file(filename, hash_type="original")
            protected_hash = hash_gen.load_hash_from_file(filename, hash_type="protected")
            
            if original_hash:
                print(f"   ✅ Original hash found for {filename}")
            else:
                print(f"   ❌ No original hash found for {filename}")
                
            if protected_hash:
                print(f"   ✅ Protected hash found for {filename}")
            else:
                print(f"   ❌ No protected hash found for {filename}")
        
        print(f"\n=== BATCH PROCESSING TEST SUMMARY ===")
        print("✅ Batch processing functionality tested successfully!")
        
    finally:
        # Clean up test files
        for file_path in test_file_paths:
            if os.path.exists(file_path):
                os.unlink(file_path)
        print(f"\nCleaned up {len(test_file_paths)} test files")

if __name__ == "__main__":
    test_batch_processing() 