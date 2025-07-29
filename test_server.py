#!/usr/bin/env python3
"""
Test script to verify the web server is working
"""

import urllib.request
import urllib.error
import time

def test_server():
    """Test if the web server is responding"""
    url = "http://localhost:8080"
    
    print("🧪 Testing web server...")
    print(f"🌐 Testing URL: {url}")
    
    try:
        # Wait a moment for server to start
        time.sleep(2)
        
        # Make a request
        response = urllib.request.urlopen(url, timeout=10)
        
        print(f"✅ Server is responding!")
        print(f"📊 Status code: {response.getcode()}")
        print(f"📄 Content type: {response.headers.get('Content-Type', 'Unknown')}")
        
        # Read a bit of the content to verify it's HTML
        content = response.read(100).decode('utf-8')
        if '<html' in content.lower():
            print("✅ Content appears to be HTML")
        else:
            print("⚠️  Content doesn't appear to be HTML")
            print(f"📄 First 100 chars: {content}")
        
        return True
        
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 Web server is working correctly!")
        print("🌐 Open your browser to: http://localhost:8080")
    else:
        print("\n❌ Web server test failed")
        print("💡 Make sure the server is running with: python simple_web_server.py") 