#!/usr/bin/env python3
"""
Test script to verify hash storage and retrieval works correctly
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.hash_generator import HashGenerator

def test_hash_storage():
    """Test hash storage and retrieval functionality."""
    print("Testing hash storage and retrieval...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for hash verification.")
        test_file_path = f.name
    
    try:
        # Initialize hash generator
        hash_gen = HashGenerator()
        
        # Test 1: Generate and save original hash
        print(f"\n1. Testing original hash generation for: {os.path.basename(test_file_path)}")
        original_hash = hash_gen.generate_file_hash(test_file_path)
        print(f"   Original hash: {original_hash}")
        
        # Save original hash
        success = hash_gen.save_hash_to_file(test_file_path, original_hash, hash_type="original")
        print(f"   Save original hash: {'SUCCESS' if success else 'FAILED'}")
        
        # Test 2: Generate and save protected hash
        print(f"\n2. Testing protected hash generation")
        protected_hash = hash_gen.generate_file_hash(test_file_path)  # Using same file for test
        print(f"   Protected hash: {protected_hash}")
        
        # Save protected hash
        success = hash_gen.save_hash_to_file(test_file_path, protected_hash, hash_type="protected")
        print(f"   Save protected hash: {'SUCCESS' if success else 'FAILED'}")
        
        # Test 3: Load and verify hashes
        print(f"\n3. Testing hash retrieval")
        loaded_original = hash_gen.load_hash_from_file(test_file_path, hash_type="original")
        loaded_protected = hash_gen.load_hash_from_file(test_file_path, hash_type="protected")
        
        print(f"   Loaded original hash: {loaded_original}")
        print(f"   Loaded protected hash: {loaded_protected}")
        
        # Test 4: Verify hash matching
        print(f"\n4. Testing hash verification")
        original_match = (original_hash == loaded_original)
        protected_match = (protected_hash == loaded_protected)
        
        print(f"   Original hash match: {'YES' if original_match else 'NO'}")
        print(f"   Protected hash match: {'YES' if protected_match else 'NO'}")
        
        # Test 5: Test with different filename (simulating API behavior)
        print(f"\n5. Testing with different filename (API simulation)")
        different_filename = "test_document.txt"
        success = hash_gen.save_hash_to_file(different_filename, original_hash, hash_type="original")
        print(f"   Save hash with different filename: {'SUCCESS' if success else 'FAILED'}")
        
        loaded_different = hash_gen.load_hash_from_file(different_filename, hash_type="original")
        print(f"   Loaded hash with different filename: {loaded_different}")
        
        different_match = (original_hash == loaded_different)
        print(f"   Different filename hash match: {'YES' if different_match else 'NO'}")
        
        # Summary
        print(f"\n=== TEST SUMMARY ===")
        all_tests_passed = original_match and protected_match and different_match
        print(f"All tests passed: {'YES' if all_tests_passed else 'NO'}")
        
        if all_tests_passed:
            print("✅ Hash storage system is working correctly!")
        else:
            print("❌ Hash storage system has issues!")
            
        return all_tests_passed
        
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
        print(f"\nCleaned up test file: {test_file_path}")

if __name__ == "__main__":
    test_hash_storage() 