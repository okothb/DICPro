#!/usr/bin/env python3
"""
Test script to verify web integration is working correctly
"""

import requests
import os
import tempfile
from pathlib import Path

def test_api_health():
    """Test if the API is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API is not running. Please start the FastAPI server first.")
        return False

def test_protect_endpoint():
    """Test the protect endpoint with mandatory output folder"""
    try:
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for protection")
            test_file_path = f.name
        
        # Create a test output folder
        test_output_folder = tempfile.mkdtemp()
        
        # Test the protect endpoint
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'secret_data': 'Test secret data',
                'encrypt_payload': 'false',
                'output_folder': test_output_folder
            }
            
            response = requests.post("http://localhost:8000/protect", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Protect endpoint working correctly")
                print(f"   - Success: {result.get('success')}")
                print(f"   - Original Hash: {result.get('original_hash', 'N/A')}")
                print(f"   - Protected Hash: {result.get('protected_hash', 'N/A')}")
                return True
            else:
                print(f"❌ Protect endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        if 'test_file_path' in locals():
            os.unlink(test_file_path)
        if 'test_output_folder' in locals():
            import shutil
            shutil.rmtree(test_output_folder)

def test_verify_endpoint():
    """Test the verify endpoint"""
    try:
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for verification")
            test_file_path = f.name
        
        # Test the verify endpoint
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            
            response = requests.post("http://localhost:8000/verify", files=files)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Verify endpoint working correctly")
                print(f"   - Success: {result.get('success')}")
                print(f"   - Is Verified: {result.get('is_verified')}")
                print(f"   - Current Hash: {result.get('current_hash', 'N/A')}")
                print(f"   - Stored Hash: {result.get('stored_hash', 'N/A')}")
                return True
            else:
                print(f"❌ Verify endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        if 'test_file_path' in locals():
            os.unlink(test_file_path)

def main():
    """Run all tests"""
    print("🧪 Testing Web Integration")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API health check failed. Please start the FastAPI server first.")
        print("   Run: python api.py")
        return
    
    print("\n" + "=" * 50)
    
    # Test protect endpoint
    print("\n🔒 Testing Protect Endpoint")
    test_protect_endpoint()
    
    print("\n" + "=" * 50)
    
    # Test verify endpoint
    print("\n🔍 Testing Verify Endpoint")
    test_verify_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 