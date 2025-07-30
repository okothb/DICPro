#!/usr/bin/env python3
"""
Debug script for path validation issues.
"""

import tempfile
import os
from core.path_validator import validate_folder_path, PathValidator

def test_path_validation():
    """Test path validation with detailed output."""
    
    # Create a test directory
    temp_dir = tempfile.mkdtemp()
    test_dir = os.path.join(temp_dir, "test_output")
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"Testing path: {test_dir}")
    print(f"Path exists: {os.path.exists(test_dir)}")
    print(f"Path is directory: {os.path.isdir(test_dir)}")
    print(f"Path is writable: {os.access(test_dir, os.W_OK)}")
    
    # Test the validation
    is_valid, message = validate_folder_path(test_dir)
    print(f"Valid: {is_valid}")
    print(f"Message: {message}")
    
    # Test some attack vectors
    attack_vectors = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "C:\\temp<script>alert('xss')</script>",
        "file:///etc/passwd",
        "C:\\temp; rm -rf /",
    ]
    
    print("\nTesting attack vectors:")
    for attack_path in attack_vectors:
        is_valid, message = validate_folder_path(attack_path)
        print(f"Path: {attack_path}")
        print(f"Valid: {is_valid}")
        print(f"Message: {message}")
        print("-" * 50)

if __name__ == "__main__":
    test_path_validation() 