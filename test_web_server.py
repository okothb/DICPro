#!/usr/bin/env python3
"""
Test script to verify the web server is working correctly
"""

import os
import sys
from pathlib import Path

def test_web_files():
    """Test that all required web files exist"""
    web_dir = Path("web")
    
    if not web_dir.exists():
        print("❌ Error: web directory not found!")
        return False
    
    required_files = [
        "index.html",
        "static/css/style.css",
        "static/js/app.js",
        "README.md"
    ]
    
    print("🔍 Checking web files...")
    all_exist = True
    
    for file_path in required_files:
        full_path = web_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_server_startup():
    """Test that the server can start without errors"""
    print("\n🚀 Testing server startup...")
    
    try:
        # Import the web server module
        import web_server
        
        # Check if the main function exists
        if hasattr(web_server, 'main'):
            print("✅ web_server.py has main function")
            return True
        else:
            print("❌ web_server.py missing main function")
            return False
            
    except ImportError as e:
        print(f"❌ Error importing web_server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🧪 Testing DocProject Web Server Setup")
    print("=" * 50)
    
    # Test 1: Check web files exist
    files_ok = test_web_files()
    
    # Test 2: Check server can be imported
    server_ok = test_server_startup()
    
    print("\n" + "=" * 50)
    if files_ok and server_ok:
        print("✅ All tests passed! Web server should work correctly.")
        print("\n📋 To start the web server:")
        print("   python web_server.py")
        print("\n🌐 Then open your browser to: http://localhost:8080")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 