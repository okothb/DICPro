#!/usr/bin/env python3
"""
Simple test for Netlify function import
"""

import sys
import os

# Add the netlify functions directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'netlify', 'functions'))

print("Testing import...")

try:
    from api import handler, get_cors_headers, handle_health
    print("✅ Successfully imported API handler")
    
    # Test a simple health check
    event = {
        'httpMethod': 'GET',
        'path': '/health',
        'headers': {},
        'body': ''
    }
    
    response = handle_health()
    print(f"✅ Health check response: {response['statusCode']}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("Test complete.")