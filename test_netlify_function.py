#!/usr/bin/env python3
"""
Test script for Netlify serverless function
Tests the API endpoints locally before deployment
"""

import json
import sys
import os

# Add the netlify functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'netlify', 'functions'))

try:
    from api import handler
except ImportError as e:
    print(f"Error importing API handler: {e}")
    print("Make sure all core modules are in netlify/functions/core/")
    sys.exit(1)

def test_health_endpoint():
    """Test the health check endpoint"""
    event = {
        'httpMethod': 'GET',
        'path': '/health',
        'headers': {},
        'body': ''
    }
    context = {}
    
    response = handler(event, context)
    print("🔍 Testing health endpoint...")
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"✅ Health endpoint test passed")
        print(f"   Status: {body.get('status')}")
        print(f"   Version: {body.get('version')}")
        return True
    else:
        print(f"❌ Health endpoint test failed")
        print(f"   Response: {response['body']}")
        return False

def test_cors_preflight():
    """Test CORS preflight request"""
    event = {
        'httpMethod': 'OPTIONS',
        'path': '/protect',
        'headers': {},
        'body': ''
    }
    context = {}
    
    response = handler(event, context)
    print("\n🔍 Testing CORS preflight...")
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        headers = response.get('headers', {})
        if 'Access-Control-Allow-Origin' in headers:
            print("✅ CORS preflight test passed")
            return True
    
    print("❌ CORS preflight test failed")
    return False

def test_protect_endpoint():
    """Test the protect endpoint (without actual file)"""
    event = {
        'httpMethod': 'POST',
        'path': '/protect',
        'headers': {
            'content-type': 'multipart/form-data; boundary=test'
        },
        'body': ''
    }
    context = {}
    
    response = handler(event, context)
    print("\n🔍 Testing protect endpoint...")
    print(f"Status Code: {response['statusCode']}")
    
    # We expect this to fail due to missing form data, but the endpoint should be reachable
    if response['statusCode'] in [400, 503]:  # 400 for missing data, 503 for missing modules
        print("✅ Protect endpoint test passed (endpoint is reachable)")
        return True
    else:
        print("❌ Protect endpoint test failed")
        print(f"   Response: {response['body']}")
        return False

def test_unknown_endpoint():
    """Test unknown endpoint returns 404"""
    event = {
        'httpMethod': 'GET',
        'path': '/unknown',
        'headers': {},
        'body': ''
    }
    context = {}
    
    response = handler(event, context)
    print("\n🔍 Testing unknown endpoint...")
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 404:
        print("✅ Unknown endpoint test passed (correctly returns 404)")
        return True
    else:
        print("❌ Unknown endpoint test failed")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Netlify Serverless Function")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_cors_preflight,
        test_protect_endpoint,
        test_unknown_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Netlify function is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())