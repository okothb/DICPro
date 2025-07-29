#!/usr/bin/env python3
"""
Simple startup script for DocProject web server
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting DocProject Web Server")
    print("=" * 50)
    
    # Check if web directory exists
    web_dir = Path("web").resolve()
    if not web_dir.exists():
        print("❌ Error: web directory not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if index.html exists
    index_file = web_dir / "index.html"
    if not index_file.exists():
        print("❌ Error: index.html not found in web directory!")
        sys.exit(1)
    
    print("✅ Web directory and files found")
    print(f"📁 Web directory: {web_dir}")
    print(f"📄 Index file: {index_file}")
    
    # Start the server using Python's built-in server
    print("\n🌐 Starting web server on http://localhost:8080")
    print("📋 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Change to web directory first
        original_dir = os.getcwd()
        os.chdir(str(web_dir))
        print(f"📁 Changed to directory: {os.getcwd()}")
        
        # Use Python's built-in HTTP server
        subprocess.run([
            sys.executable, "-m", "http.server", "8080"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print(f"💡 Try running manually: cd {web_dir} && python -m http.server 8080")
        sys.exit(1)
    finally:
        # Change back to original directory
        try:
            os.chdir(original_dir)
        except:
            pass

if __name__ == "__main__":
    main() 