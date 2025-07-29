#!/usr/bin/env python3
"""
Simple test for web app import
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Simple import test."""
    print("Testing web app import...")
    
    try:
        # Test basic imports
        import flet as ft
        print("✅ Flet imported successfully")
        
        from core.encryptor import DocumentEncryptor
        print("✅ DocumentEncryptor imported successfully")
        
        from core.hash_generator import HashGenerator
        print("✅ HashGenerator imported successfully")
        
        from core.verifier import DocumentVerifier
        print("✅ DocumentVerifier imported successfully")
        
        # Test web app import
        from web_app import DocumentProtectionWebApp
        print("✅ WebApp imported successfully")
        
        # Test instantiation
        app = DocumentProtectionWebApp()
        print("✅ WebApp instantiated successfully")
        
        print("\n🎉 All tests passed! Web app should work now.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 