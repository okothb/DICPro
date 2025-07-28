#!/usr/bin/env python3
"""
DocProject API Server Startup Script
Starts the FastAPI server with proper configuration for production use.
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the DocProject API server"""
    
    # Configuration
    host = os.getenv("DOCPROJECT_HOST", "0.0.0.0")
    port = int(os.getenv("DOCPROJECT_PORT", "8000"))
    reload = os.getenv("DOCPROJECT_RELOAD", "false").lower() == "true"
    log_level = os.getenv("DOCPROJECT_LOG_LEVEL", "info")
    
    # Create temp directory if it doesn't exist
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("DocProject API Server")
    print("Document Protection and Verification API")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log Level: {log_level}")
    print("=" * 60)
    print("API Documentation:")
    print(f"  Swagger UI: http://{host}:{port}/docs")
    print(f"  ReDoc: http://{host}:{port}/redoc")
    print(f"  Health Check: http://{host}:{port}/health")
    print("=" * 60)
    print("Starting server...")
    print()
    
    try:
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 