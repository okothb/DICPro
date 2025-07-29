#!/usr/bin/env python3
"""
Ultra-simple web server for DocProject - Windows compatible
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Starting DocProject Web Server (Simple)")
    print("=" * 50)
    
    # Get the web directory path
    current_dir = Path.cwd()
    web_dir = current_dir / "web"
    
    if not web_dir.exists():
        print("❌ Error: web directory not found!")
        print(f"Current directory: {current_dir}")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    print(f"✅ Web directory found: {web_dir}")
    
    # Check for index.html
    index_file = web_dir / "index.html"
    if not index_file.exists():
        print("❌ Error: index.html not found!")
        sys.exit(1)
    
    print(f"✅ Index file found: {index_file}")
    
    # Change to web directory
    try:
        os.chdir(str(web_dir))
        print(f"📁 Changed to: {os.getcwd()}")
    except Exception as e:
        print(f"❌ Error changing directory: {e}")
        sys.exit(1)
    
    print("\n🌐 Starting server on http://localhost:8080")
    print("📋 Press Ctrl+C to stop")
    print("-" * 50)
    
    # Start the server
    try:
        os.system(f"{sys.executable} -m http.server 8080")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main() 