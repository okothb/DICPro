#!/usr/bin/env python3
"""
Simple test to verify web app starts correctly
"""

import sys
import os
import time
import threading

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_web_app_start():
    """Test that web app can start without errors."""
    print("🧪 Testing web app startup...")
    
    try:
        from web_app import DocumentProtectionWebApp
        import flet as ft
        
        # Create app instance
        app = DocumentProtectionWebApp()
        print("✅ WebApp instance created successfully")
        
        # Test page initialization (without actually starting the server)
        def test_page_init(page):
            try:
                app.main(page)
                print("✅ Page initialization successful")
                return True
            except Exception as e:
                print(f"❌ Page initialization failed: {e}")
                return False
        
        # Create a mock page for testing
        class MockPage:
            def __init__(self):
                self.title = ""
                self.theme_mode = None
                self.window_width = 0
                self.window_height = 0
                self.padding = 0
                self.spacing = 0
                self.app_bar = None
                self.overlay = []
                self.views = []
                self.on_route_change = None
            
            def update(self):
                pass
            
            def show_snack_bar(self, snack_bar):
                pass
        
        mock_page = MockPage()
        success = test_page_init(mock_page)
        
        if success:
            print("✅ Web app initialization test passed")
            return True
        else:
            print("❌ Web app initialization test failed")
            return False
            
    except Exception as e:
        print(f"❌ Web app test failed: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Testing Web Application Startup")
    print("=" * 40)
    
    if test_web_app_start():
        print("\n" + "=" * 40)
        print("🎉 Web app startup test passed!")
        print("\nThe web application should now work correctly.")
        print("To start it, run: python start_web_app.py")
    else:
        print("\n" + "=" * 40)
        print("❌ Web app startup test failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main() 