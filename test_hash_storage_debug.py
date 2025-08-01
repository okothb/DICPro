#!/usr/bin/env python3
"""
Debug script for hash storage and retrieval issues.
"""

import os
import tempfile
from core.hash_generator import HashGenerator

def test_hash_storage_and_retrieval():
    """Test hash storage and retrieval with detailed output."""
    
    # Create a test file
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test_document.pdf")
    
    # Create a simple test file
    with open(test_file, 'w') as f:
        f.write("This is a test document for hash verification.")
    
    print(f"Test file created: {test_file}")
    print(f"File exists: {os.path.exists(test_file)}")
    
    # Initialize hash generator
    hash_gen = HashGenerator()
    print(f"Hash directory: {hash_gen.hash_dir}")
    print(f"Hash directory exists: {os.path.exists(hash_gen.hash_dir)}")
    
    # Test hash generation
    original_hash = hash_gen.generate_file_hash(test_file)
    print(f"Original hash: {original_hash}")
    
    # Test hash storage
    filename = "test_document.pdf"
    print(f"\nTesting hash storage with filename: {filename}")
    
    # Save original hash
    success_original = hash_gen.save_hash_to_file(filename, original_hash, "original")
    print(f"Original hash saved: {success_original}")
    
    # Save protected hash (simulate protected file)
    protected_hash = "protected_hash_value_for_testing"
    success_protected = hash_gen.save_hash_to_file(filename, protected_hash, "protected")
    print(f"Protected hash saved: {success_protected}")
    
    # List files in hash directory
    print(f"\nFiles in hash directory:")
    if os.path.exists(hash_gen.hash_dir):
        for file in os.listdir(hash_gen.hash_dir):
            print(f"  - {file}")
    else:
        print("  Hash directory does not exist!")
    
    # Test hash retrieval
    print(f"\nTesting hash retrieval with filename: {filename}")
    retrieved_original = hash_gen.load_hash_from_file(filename, "original")
    retrieved_protected = hash_gen.load_hash_from_file(filename, "protected")
    
    print(f"Retrieved original hash: {retrieved_original}")
    print(f"Retrieved protected hash: {retrieved_protected}")
    
    # Test with full path
    print(f"\nTesting hash retrieval with full path: {test_file}")
    retrieved_original_full = hash_gen.load_hash_from_file(test_file, "original")
    retrieved_protected_full = hash_gen.load_hash_from_file(test_file, "protected")
    
    print(f"Retrieved original hash (full path): {retrieved_original_full}")
    print(f"Retrieved protected hash (full path): {retrieved_protected_full}")
    
    # Test the expected hash file paths
    base_name = os.path.splitext(os.path.basename(filename))[0]
    original_hash_file = f"{base_name}_original.hash.json"
    protected_hash_file = f"{base_name}_protected.hash.json"
    
    original_hash_path = os.path.join(hash_gen.hash_dir, original_hash_file)
    protected_hash_path = os.path.join(hash_gen.hash_dir, protected_hash_file)
    
    print(f"\nExpected hash file paths:")
    print(f"Original hash file: {original_hash_path}")
    print(f"Original hash file exists: {os.path.exists(original_hash_path)}")
    print(f"Protected hash file: {protected_hash_path}")
    print(f"Protected hash file exists: {os.path.exists(protected_hash_path)}")

if __name__ == "__main__":
    test_hash_storage_and_retrieval() 