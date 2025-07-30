#!/usr/bin/env python3
"""
Test script for the API endpoint.
"""

import requests
import json

def test_api_endpoint():
    """Test the validate-path API endpoint."""
    
    # Test with a safe path
    safe_path = "C:\\Users\\Hp\\Documents"
    data = {'path': safe_path}
    
    try:
        response = requests.post('http://localhost:8000/api/validate-path', data=data)
        print(f"Safe path test:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("API server not running. Start the server first.")
        return
    
    # Test with an attack vector
    attack_path = "../../../etc/passwd"
    data = {'path': attack_path}
    
    try:
        response = requests.post('http://localhost:8000/api/validate-path', data=data)
        print(f"Attack vector test:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("API server not running.")
        return

if __name__ == "__main__":
    test_api_endpoint() 