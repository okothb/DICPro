#!/usr/bin/env python3
"""
Simple web server to serve the DocProject web interface
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class DocProjectHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=".", **kwargs)
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging format
        print(f"[Web Server] {format % args}")

def main():
    # Check if web directory exists
    web_dir = Path("web")
    if not web_dir.exists():
        print("Error: web directory not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Change to web directory
    os.chdir(web_dir)
    print(f"📁 Changed to directory: {os.getcwd()}")
    
    # Server configuration
    PORT = 8080
    HOST = "localhost"
    
    print(f"🚀 Starting DocProject Web Server")
    print(f"📁 Serving files from: {web_dir.absolute()}")
    print(f"🌐 Web interface available at: http://{HOST}:{PORT}")
    print(f"🔗 API should be running at: http://localhost:8000")
    print(f"📋 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        with socketserver.TCPServer((HOST, PORT), DocProjectHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully on {HOST}:{PORT}")
            print(f"📖 Open your browser and navigate to: http://{HOST}:{PORT}")
            print(f"📄 Serving index.html from: {os.path.join(os.getcwd(), 'index.html')}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {PORT} is already in use!")
            print(f"💡 Try using a different port or stop the existing server")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 