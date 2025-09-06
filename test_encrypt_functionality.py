#!/usr/bin/env python3
"""
Simple test server to verify encrypt checkbox functionality
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def start_test_server():
    # Change to web directory
    web_dir = Path("web")
    if web_dir.exists():
        os.chdir(web_dir)
    
    PORT = 8080
    
    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Test server running at http://localhost:{PORT}")
        print("Opening app.html in browser...")
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}/app.html")
        
        print("Check the encrypt payload checkbox functionality!")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    start_test_server()