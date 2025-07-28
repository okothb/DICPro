#!/usr/bin/env python3
"""
DocProject API Test Script
Tests the API endpoints and functionality.
"""

import requests
import json
import time
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("test_files")
TEST_FILES_DIR.mkdir(exist_ok=True)

def create_test_files():
    """Create test files for API testing"""
    test_files = {}
    
    # Create a simple text file
    text_file = TEST_FILES_DIR / "test.txt"
    with open(text_file, 'w') as f:
        f.write("This is a test document for API testing.")
    test_files['text'] = str(text_file)
    
    # Create a simple CSV file (Excel-compatible)
    csv_file = TEST_FILES_DIR / "test.csv"
    with open(csv_file, 'w') as f:
        f.write("Name,Age,City\nJohn,30,New York\nJane,25,Los Angeles")
    test_files['csv'] = str(csv_file)
    
    return test_files

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Health check passed: {data['status']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        response.raise_for_status()
        data = response.json()
        print(f"✓ Root endpoint: {data['message']}")
        return True
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        return False

def test_protect_endpoint(test_files):
    """Test document protection endpoint"""
    print("Testing protect endpoint...")
    try:
        # Test with CSV file
        with open(test_files['csv'], 'rb') as f:
            files = {'file': ('test.csv', f, 'text/csv')}
            data = {
                'secret_data': 'API test secret message',
                'encrypt_payload': False
            }
            response = requests.post(f"{API_BASE_URL}/protect", files=files, data=data)
            response.raise_for_status()
            result = response.json()
            
            print(f"✓ Protection successful: {result['message']}")
            print(f"  Method: {result['method']}")
            print(f"  Original Hash: {result['original_hash'][:16]}...")
            print(f"  Protected Hash: {result['protected_hash'][:16]}...")
            
            return result['protected_file']
    except Exception as e:
        print(f"✗ Protection failed: {e}")
        return None

def test_verify_endpoint(protected_file_path):
    """Test document verification endpoint"""
    print("Testing verify endpoint...")
    try:
        with open(protected_file_path, 'rb') as f:
            files = {'file': ('protected_test.csv', f, 'text/csv')}
            response = requests.post(f"{API_BASE_URL}/verify", files=files)
            response.raise_for_status()
            result = response.json()
            
            print(f"✓ Verification successful: {result['message']}")
            print(f"  Verified: {result['is_verified']}")
            print(f"  Current Hash: {result['current_hash'][:16]}...")
            print(f"  Stored Hash: {result['stored_hash'][:16]}...")
            
            return result['is_verified']
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def test_extract_endpoint(protected_file_path):
    """Test data extraction endpoint"""
    print("Testing extract endpoint...")
    try:
        with open(protected_file_path, 'rb') as f:
            files = {'file': ('protected_test.csv', f, 'text/csv')}
            response = requests.post(f"{API_BASE_URL}/extract", files=files)
            response.raise_for_status()
            result = response.json()
            
            print(f"✓ Extraction successful: {result['message']}")
            print(f"  Extracted Data: {result['extracted_data']}")
            print(f"  Hashes Match: {result['hashes_match']}")
            
            return result['extracted_data'] == 'API test secret message'
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False

def test_batch_protect_endpoint(test_files):
    """Test batch protection endpoint"""
    print("Testing batch protect endpoint...")
    try:
        files = []
        for file_type, file_path in test_files.items():
            with open(file_path, 'rb') as f:
                files.append(('files', (f"test_{file_type}.{file_type}", f, 'application/octet-stream')))
        
        data = {
            'secret_data': 'Batch API test message',
            'encrypt_payload': False
        }
        
        response = requests.post(f"{API_BASE_URL}/batch-protect", files=files, data=data)
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Batch protection successful: {result['message']}")
        print(f"  Total Files: {result['total_files']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        
        return result['successful'] > 0
    except Exception as e:
        print(f"✗ Batch protection failed: {e}")
        return False

def test_cleanup_endpoint():
    """Test cleanup endpoint"""
    print("Testing cleanup endpoint...")
    try:
        response = requests.delete(f"{API_BASE_URL}/cleanup")
        response.raise_for_status()
        result = response.json()
        
        print(f"✓ Cleanup successful: {result['message']}")
        return True
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("=" * 60)
    print("DocProject API Test Suite")
    print("=" * 60)
    
    # Check if API server is running
    try:
        requests.get(f"{API_BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print("✗ API server is not running!")
        print("Please start the API server first:")
        print("  python start_api.py")
        return
    
    # Create test files
    print("Creating test files...")
    test_files = create_test_files()
    
    # Run tests
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Batch Protection", lambda: test_batch_protect_endpoint(test_files)),
        ("Cleanup", test_cleanup_endpoint),
    ]
    
    # Test protection and verification flow
    protected_file = test_protect_endpoint(test_files)
    if protected_file:
        test_verify_endpoint(protected_file)
        test_extract_endpoint(protected_file)
    
    print("\n" + "=" * 60)
    print("API Test Summary")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✓ {test_name}: PASSED")
                passed += 1
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the API implementation.")
    
    # Cleanup test files
    print("\nCleaning up test files...")
    for file_path in test_files.values():
        try:
            os.remove(file_path)
        except:
            pass
    
    print("Test completed!")

if __name__ == "__main__":
    main() 