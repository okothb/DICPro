#!/usr/bin/env python3
"""
Local test script for Netlify function
Tests the API endpoints without deploying to Netlify
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Import the Netlify function
from netlify.functions.api import handler

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing Health Endpoint...")
    
    event = {
        'httpMethod': 'GET',
        'path': '/health',
        'headers': {},
        'body': ''
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    print(f"Headers: {response['headers']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Health endpoint test PASSED")
        return True
    else:
        print(f"❌ Health endpoint test FAILED: {response['body']}")
        return False

def test_cors_preflight():
    """Test CORS preflight request"""
    print("\n🔍 Testing CORS Preflight...")
    
    event = {
        'httpMethod': 'OPTIONS',
        'path': '/protect',
        'headers': {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        },
        'body': ''
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    print(f"Headers: {response['headers']}")
    
    if response['statusCode'] == 200:
        headers = response['headers']
        if 'Access-Control-Allow-Origin' in headers:
            print("✅ CORS preflight test PASSED")
            return True
        else:
            print("❌ CORS preflight test FAILED: Missing CORS headers")
            return False
    else:
        print(f"❌ CORS preflight test FAILED: {response['body']}")
        return False

def test_verify_endpoint():
    """Test the verify endpoint"""
    print("\n🔍 Testing Verify Endpoint...")
    
    event = {
        'httpMethod': 'POST',
        'path': '/verify',
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps({
            'file_path': 'test_document.pdf'
        })
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Verify endpoint test PASSED")
        return True
    else:
        print(f"❌ Verify endpoint test FAILED: {response['body']}")
        return False

def test_extract_endpoint():
    """Test the extract endpoint"""
    print("\n🔍 Testing Extract Endpoint...")
    
    event = {
        'httpMethod': 'POST',
        'path': '/extract',
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps({
            'file_path': 'test_document.pdf'
        })
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Extract endpoint test PASSED")
        return True
    else:
        print(f"❌ Extract endpoint test FAILED: {response['body']}")
        return False

def test_batch_protect_endpoint():
    """Test the batch protect endpoint"""
    print("\n🔍 Testing Batch Protect Endpoint...")
    
    event = {
        'httpMethod': 'POST',
        'path': '/batch-protect',
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps({
            'files': ['doc1.pdf', 'doc2.pdf'],
            'secret_data': 'test secret'
        })
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Batch protect endpoint test PASSED")
        return True
    else:
        print(f"❌ Batch protect endpoint test FAILED: {response['body']}")
        return False

def test_batch_verify_endpoint():
    """Test the batch verify endpoint"""
    print("\n🔍 Testing Batch Verify Endpoint...")
    
    event = {
        'httpMethod': 'POST',
        'path': '/batch-verify',
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps({
            'files': ['doc1.pdf', 'doc2.pdf']
        })
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Batch verify endpoint test PASSED")
        return True
    else:
        print(f"❌ Batch verify endpoint test FAILED: {response['body']}")
        return False

def test_validate_path_endpoint():
    """Test the validate path endpoint"""
    print("\n🔍 Testing Validate Path Endpoint...")
    
    event = {
        'httpMethod': 'POST',
        'path': '/validate-path',
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps({
            'path': '/tmp/output'
        })
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Validate path endpoint test PASSED")
        return True
    else:
        print(f"❌ Validate path endpoint test FAILED: {response['body']}")
        return False

def test_404_endpoint():
    """Test 404 handling"""
    print("\n🔍 Testing 404 Handling...")
    
    event = {
        'httpMethod': 'GET',
        'path': '/nonexistent',
        'headers': {},
        'body': ''
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 404:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ 404 handling test PASSED")
        return True
    else:
        print(f"❌ 404 handling test FAILED: Expected 404, got {response['statusCode']}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Netlify Function Tests")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_cors_preflight,
        test_verify_endpoint,
        test_extract_endpoint,
        test_batch_protect_endpoint,
        test_batch_verify_endpoint,
        test_validate_path_endpoint,
        test_404_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! Netlify function is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests FAILED. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)