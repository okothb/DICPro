#!/usr/bin/env python3
"""
Simple API test to verify the Netlify function works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the Netlify environment
from netlify.functions.api import handler

def test_basic_endpoints():
    """Test basic API endpoints"""
    
    # Test health endpoint
    health_event = {
        'httpMethod': 'GET',
        'path': '/.netlify/functions/api/health',
        'headers': {},
        'body': None
    }
    
    print("Testing health endpoint...")
    response = handler(health_event, {})
    print(f"Health response: {response}")
    
    # Test test endpoint
    test_event = {
        'httpMethod': 'GET', 
        'path': '/.netlify/functions/api/test',
        'headers': {},
        'body': None
    }
    
    print("\nTesting test endpoint...")
    response = handler(test_event, {})
    print(f"Test response: {response}")

if __name__ == "__main__":
    test_basic_endpoints()