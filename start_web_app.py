#!/usr/bin/env python3
"""
Launcher script for Document Integrity Protection System Web Application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the web application."""
    try:
        from web_app import main as web_main
        print("🚀 Starting Document Protection Web Application...")
        print("📱 Opening in your default web browser...")
        print("🔗 The application will be available at: http://localhost:8550")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 50)
        
        web_main()
        
    except ImportError as e:
        print(f"❌ Error importing required modules: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Web application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 