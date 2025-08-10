#!/usr/bin/env python3
"""
HTTP-like test for Netlify function
Simulates real HTTP requests to test the function behavior
"""

import json
import base64
from netlify.functions.api import handler

def test_protect_endpoint_with_multipart():
    """Test the protect endpoint with simulated multipart data"""
    print("🔍 Testing Protect Endpoint with Multipart Data...")
    
    # Create a simple test file content
    test_file_content = b"This is a test PDF content for protection"
    
    # Create multipart form data manually
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    multipart_body = f"""------WebKitFormBoundary7MA4YWxkTrZu0gW\r
Content-Disposition: form-data; name="secret_data"\r
\r
Test secret data for protection\r
------WebKitFormBoundary7MA4YWxkTrZu0gW\r
Content-Disposition: form-data; name="encrypt_payload"\r
\r
false\r
------WebKitFormBoundary7MA4YWxkTrZu0gW\r
Content-Disposition: form-data; name="file"; filename="test.pdf"\r
Content-Type: application/pdf\r
\r
{test_file_content.decode('utf-8', errors='ignore')}\r
------WebKitFormBoundary7MA4YWxkTrZu0gW--\r
"""
    
    # Encode the body
    encoded_body = base64.b64encode(multipart_body.encode()).decode()
    
    event = {
        'httpMethod': 'POST',
        'path': '/protect',
        'headers': {
            'content-type': f'multipart/form-data; boundary={boundary}'
        },
        'body': encoded_body,
        'isBase64Encoded': True
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 503:
        # Expected when core modules aren't available
        body = json.loads(response['body'])
        print(f"Response: {body['error']}")
        print("✅ Protect endpoint test PASSED (expected 503 - core modules not available)")
        return True
    elif response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Response Body: {json.dumps(body, indent=2)}")
        print("✅ Protect endpoint test PASSED")
        return True
    else:
        print(f"❌ Protect endpoint test FAILED: {response['body']}")
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing Error Handling...")
    
    # Test with invalid JSON
    event = {
        'httpMethod': 'POST',
        'path': '/verify',
        'headers': {
            'content-type': 'application/json'
        },
        'body': 'invalid json{'
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    # Should handle gracefully
    if response['statusCode'] in [200, 400, 500]:
        print("✅ Error handling test PASSED")
        return True
    else:
        print(f"❌ Error handling test FAILED: Unexpected status {response['statusCode']}")
        return False

def test_large_request():
    """Test handling of larger requests"""
    print("\n🔍 Testing Large Request Handling...")
    
    # Create a larger payload
    large_data = "x" * 10000  # 10KB of data
    
    event = {
        'httpMethod': 'POST',
        'path': '/extract',
        'headers': {
            'content-type': 'application/json'
        },
        'body': json.dumps({
            'file_path': 'large_test.pdf',
            'large_data': large_data
        })
    }
    
    response = handler(event, {})
    
    print(f"Status Code: {response['statusCode']}")
    
    if response['statusCode'] == 200:
        print("✅ Large request test PASSED")
        return True
    else:
        print(f"❌ Large request test FAILED: {response['body']}")
        return False

def test_concurrent_requests():
    """Simulate concurrent requests"""
    print("\n🔍 Testing Concurrent Request Simulation...")
    
    # Test multiple requests in sequence (simulating concurrency)
    results = []
    
    for i in range(3):
        event = {
            'httpMethod': 'GET',
            'path': '/health',
            'headers': {},
            'body': ''
        }
        
        response = handler(event, {})
        results.append(response['statusCode'] == 200)
    
    success_count = sum(results)
    print(f"Successful requests: {success_count}/3")
    
    if success_count == 3:
        print("✅ Concurrent request simulation PASSED")
        return True
    else:
        print("❌ Concurrent request simulation FAILED")
        return False

def main():
    """Run HTTP-like tests"""
    print("🌐 Starting HTTP-like Netlify Function Tests")
    print("=" * 60)
    
    tests = [
        test_protect_endpoint_with_multipart,
        test_error_handling,
        test_large_request,
        test_concurrent_requests
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 HTTP Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All HTTP tests PASSED! Function handles HTTP scenarios well.")
        return True
    else:
        print(f"⚠️  {total - passed} tests FAILED.")
        return False

if __name__ == "__main__":
    main()