#!/usr/bin/env python3
"""
Integration test to verify security validation in API endpoints
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
import requests
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_security_validation():
    """Test that the API properly validates secret data"""
    
    print("🔒 Testing API Security Validation")
    print("=" * 50)
    
    # Start the API server (you would need to run this separately)
    api_url = "http://localhost:8000"
    
    # Test cases for API validation
    test_cases = [
        {
            "name": "Valid secret data",
            "secret_data": "Hello World - This is safe text and numbers 123",
            "should_accept": True
        },
        {
            "name": "Script injection attempt",
            "secret_data": "<script>alert('xss')</script>",
            "should_accept": False
        },
        {
            "name": "JavaScript protocol",
            "secret_data": "javascript:alert('xss')",
            "should_accept": False
        },
        {
            "name": "Command execution attempt",
            "secret_data": "cmd /c dir",
            "should_accept": False
        },
        {
            "name": "SQL injection attempt",
            "secret_data": "SELECT * FROM users",
            "should_accept": False
        },
        {
            "name": "URL attempt",
            "secret_data": "http://malicious.com",
            "should_accept": False
        },
        {
            "name": "Empty data",
            "secret_data": "",
            "should_accept": False
        },
        {
            "name": "Only whitespace",
            "secret_data": "   \t\n   ",
            "should_accept": False
        },
        {
            "name": "Too long data",
            "secret_data": "A" * 10001,
            "should_accept": False
        }
    ]
    
    print("\n📋 Testing API Endpoints:")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  {i}. {test_case['name']}")
        print(f"     Data: {repr(test_case['secret_data'][:50])}{'...' if len(test_case['secret_data']) > 50 else ''}")
        
        # Create a simple test file
        test_file_content = "This is a test document for security validation."
        test_file_path = f"test_security_{i}.txt"
        
        with open(test_file_path, 'w') as f:
            f.write(test_file_content)
        
        try:
            # Test the protect endpoint
            with open(test_file_path, 'rb') as f:
                files = {'file': (test_file_path, f, 'text/plain')}
                data = {
                    'secret_data': test_case['secret_data'],
                    'encrypt_payload': False,
                    'output_folder': tempfile.gettempdir()
                }
                
                response = requests.post(f"{api_url}/protect", files=files, data=data)
                
                if response.status_code == 200:
                    if test_case['should_accept']:
                        print("     ✅ PASS: Accepted when it should be")
                    else:
                        print("     ❌ FAIL: Accepted when it should be rejected")
                elif response.status_code == 400:
                    error_detail = response.json().get('detail', 'Unknown error')
                    if not test_case['should_accept']:
                        print(f"     ✅ PASS: Correctly rejected - {error_detail}")
                    else:
                        print(f"     ❌ FAIL: Rejected when it should be accepted - {error_detail}")
                else:
                    print(f"     ⚠️  UNEXPECTED: Status {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            print("     ⚠️  SKIP: API server not running (start with 'python api.py')")
        except Exception as e:
            print(f"     ❌ ERROR: {str(e)}")
        finally:
            # Clean up test file
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
    
    print("\n" + "=" * 50)
    print("✅ API security validation tests completed!")
    print("\n💡 To test with the API server running:")
    print("   1. Start the API: python api.py")
    print("   2. Run this test: python test_security_integration.py")

def test_frontend_validation():
    """Test the frontend JavaScript validation"""
    
    print("\n🌐 Testing Frontend Validation")
    print("=" * 50)
    
    # Simulate the JavaScript validation logic
    def validate_secret_data_js(secret_data):
        # Check for empty data
        if not secret_data:
            return False, "Secret data cannot be empty."
        
        # Check for excessive whitespace
        if secret_data.trim().length === 0:
            return False, "Secret data cannot be empty or contain only whitespace."
        
        # Check length limits
        if secret_data.length > 10000:
            return False, "Secret data is too long. Maximum allowed length is 10,000 characters."
        
        # Define allowed characters
        allowed_chars = re.compile(r'^[a-zA-Z0-9\s.,!?;:()\[\]{}"\'\-_@#$%&*+=<>/~]*$')
        
        # Malicious patterns
        malicious_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'data:text/html', re.IGNORECASE),
            re.compile(r'data:application/x-javascript', re.IGNORECASE),
            re.compile(r'(cmd|powershell|bash|sh)\s+/[ck]', re.IGNORECASE),
            re.compile(r'exec\s*\(', re.IGNORECASE),
            re.compile(r'eval\s*\(', re.IGNORECASE),
            re.compile(r'system\s*\(', re.IGNORECASE),
            re.compile(r'(http|https|ftp)://', re.IGNORECASE),
            re.compile(r'file://', re.IGNORECASE),
            re.compile(r'\\\\([a-zA-Z0-9\-\.]+)\\\\', re.IGNORECASE),
            re.compile(r'(union|select|insert|update|delete|drop|create|alter)\s+', re.IGNORECASE),
            re.compile(r'--\s*$', re.MULTILINE),
            re.compile(r'/\*.*?\*/', re.DOTALL),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'<iframe', re.IGNORECASE),
            re.compile(r'<object', re.IGNORECASE),
            re.compile(r'<embed', re.IGNORECASE),
            re.compile(r'^MZ\s*', re.IGNORECASE),
            re.compile(r'^PE\s*', re.IGNORECASE),
            re.compile(r'^ELF\s*', re.IGNORECASE)
        ]
        
        # Check for malicious patterns
        for pattern in malicious_patterns:
            if pattern.search(secret_data):
                return False, f"Contains potentially malicious content: {pattern.pattern}"
        
        # Check for disallowed characters
        if not allowed_chars.match(secret_data):
            disallowed_chars = [char for char in secret_data if not allowed_chars.match(char)]
            return False, f"Contains disallowed characters: {''.join(set(disallowed_chars))}"
        
        return True, ""
    
    # Test cases
    test_cases = [
        ("Hello World", True),
        ("<script>alert('xss')</script>", False),
        ("javascript:alert('xss')", False),
        ("", False),
        ("   \t\n   ", False),
        ("A" * 10001, False),
    ]
    
    for i, (test_data, should_accept) in enumerate(test_cases, 1):
        is_valid, error = validate_secret_data_js(test_data)
        status = "PASS" if (is_valid == should_accept) else "FAIL"
        print(f"  {i}. {status}: {repr(test_data[:50])}{'...' if len(test_data) > 50 else ''}")
        if not is_valid and should_accept:
            print(f"       Error: {error}")
        elif is_valid and not should_accept:
            print(f"       Should have been rejected")

if __name__ == "__main__":
    test_api_security_validation()
    test_frontend_validation() 