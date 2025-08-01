#!/usr/bin/env python3
"""
Test script to simulate web verification process.
"""

import os
import tempfile
from core.hash_generator import HashGenerator

def test_web_verification_simulation():
    """Simulate the web verification process to identify the issue."""
    
    # Initialize hash generator
    hash_gen = HashGenerator()
    
    # Simulate the protect process (what happens when a file is protected)
    print("=== SIMULATING PROTECT PROCESS ===")
    original_filename = "test_document.pdf"
    original_hash = "original_hash_value_123"
    protected_hash = "protected_hash_value_456"
    
    print(f"Original filename: {original_filename}")
    print(f"Original hash: {original_hash}")
    print(f"Protected hash: {protected_hash}")
    
    # Save hashes (this is what happens in the protect endpoint)
    success_original = hash_gen.save_hash_to_file(original_filename, original_hash, "original")
    success_protected = hash_gen.save_hash_to_file(original_filename, protected_hash, "protected")
    
    print(f"Original hash saved: {success_original}")
    print(f"Protected hash saved: {success_protected}")
    
    # List hash files
    print(f"\nHash files in directory:")
    if os.path.exists(hash_gen.hash_dir):
        for file in os.listdir(hash_gen.hash_dir):
            if "test_document" in file:
                print(f"  - {file}")
    
    # Simulate the verify process (what happens when a file is verified)
    print("\n=== SIMULATING VERIFY PROCESS ===")
    
    # Test different filename scenarios that might occur in web verification
    test_filenames = [
        "test_document.pdf",  # Exact match
        "test_document_protected.pdf",  # Protected file name
        "TEST_DOCUMENT.PDF",  # Different case
        "test_document.PDF",  # Different case extension
        "test_document",  # No extension
        "test_document.txt",  # Wrong extension
        "uploaded_test_document.pdf",  # Different name
    ]
    
    for filename in test_filenames:
        print(f"\nTesting verification with filename: '{filename}'")
        
        # This is what happens in the verify endpoint
        stored_hash = hash_gen.load_hash_from_file(filename, hash_type="protected")
        
        if stored_hash:
            print(f"  ✅ Stored hash found: {stored_hash}")
        else:
            print(f"  ❌ No stored hash found for: {filename}")
            
            # Check what hash file would be expected
            base_name = os.path.splitext(os.path.basename(filename))[0]
            expected_hash_file = f"{base_name}_protected.hash.json"
            expected_hash_path = os.path.join(hash_gen.hash_dir, expected_hash_file)
            print(f"  Expected hash file: {expected_hash_path}")
            print(f"  Expected hash file exists: {os.path.exists(expected_hash_path)}")
    
    # Test the actual hash file that should exist
    print(f"\n=== CHECKING ACTUAL HASH FILES ===")
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    expected_hash_file = f"{base_name}_protected.hash.json"
    expected_hash_path = os.path.join(hash_gen.hash_dir, expected_hash_file)
    
    print(f"Original filename: {original_filename}")
    print(f"Base name: {base_name}")
    print(f"Expected hash file: {expected_hash_file}")
    print(f"Expected hash path: {expected_hash_path}")
    print(f"Hash file exists: {os.path.exists(expected_hash_path)}")
    
    if os.path.exists(expected_hash_path):
        with open(expected_hash_path, 'r') as f:
            import json
            hash_data = json.load(f)
            print(f"Hash file content: {hash_data}")

if __name__ == "__main__":
    test_web_verification_simulation() 