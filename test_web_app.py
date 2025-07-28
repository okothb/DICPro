#!/usr/bin/env python3
"""
Test script for Document Integrity Protection System Web Application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import flet as ft
        print("✅ Flet imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flet: {e}")
        return False
    
    try:
        from core.encryptor import DocumentEncryptor
        print("✅ DocumentEncryptor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import DocumentEncryptor: {e}")
        return False
    
    try:
        from core.hash_generator import HashGenerator
        print("✅ HashGenerator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import HashGenerator: {e}")
        return False
    
    try:
        from core.verifier import DocumentVerifier
        print("✅ DocumentVerifier imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import DocumentVerifier: {e}")
        return False
    
    try:
        from utils.logger import get_logger
        print("✅ Logger imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Logger: {e}")
        return False
    
    try:
        from web_app import DocumentProtectionWebApp
        print("✅ WebApp imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WebApp: {e}")
        return False
    
    return True

def test_core_functionality():
    """Test basic core functionality."""
    print("\n🔧 Testing core functionality...")
    
    try:
        from core.encryptor import DocumentEncryptor
        from core.hash_generator import HashGenerator
        from core.verifier import DocumentVerifier
        
        # Test encryptor
        encryptor = DocumentEncryptor()
        print("✅ DocumentEncryptor initialized")
        
        # Test hash generator
        hash_gen = HashGenerator()
        print("✅ HashGenerator initialized")
        
        # Test verifier
        verifier = DocumentVerifier()
        print("✅ DocumentVerifier initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False

def test_web_app_initialization():
    """Test web app initialization."""
    print("\n🌐 Testing web app initialization...")
    
    try:
        from web_app import DocumentProtectionWebApp
        
        app = DocumentProtectionWebApp()
        print("✅ WebApp initialized successfully")
        
        # Test basic properties
        assert app.current_user is None
        assert app.is_authenticated is False
        assert app.current_page == "landing"
        print("✅ WebApp properties initialized correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ WebApp initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Web Application Tests")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your dependencies.")
        sys.exit(1)
    
    # Test core functionality
    if not test_core_functionality():
        print("\n❌ Core functionality tests failed.")
        sys.exit(1)
    
    # Test web app initialization
    if not test_web_app_initialization():
        print("\n❌ Web app initialization tests failed.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Web application is ready to run.")
    print("\nTo start the web application, run:")
    print("   python start_web_app.py")
    print("\nOr to run the main application:")
    print("   python app.py")

if __name__ == "__main__":
    main() 