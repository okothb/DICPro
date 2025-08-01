#!/usr/bin/env python3
"""
Comprehensive test for web verification hash lookup fix.
"""

import os
import tempfile
from core.hash_generator import HashGenerator

def test_web_verification_fix():
    """Test the complete web verification process with various filename scenarios."""
    
    print("=== WEB VERIFICATION HASH LOOKUP FIX TEST ===\n")
    
    # Initialize hash generator
    hash_gen = HashGenerator()
    
    # Simulate protecting a document (what happens in the web interface)
    print("1. SIMULATING DOCUMENT PROTECTION")
    original_filename = "important_document.pdf"
    original_hash = "original_hash_123456789"
    protected_hash = "protected_hash_987654321"
    
    print(f"   Original filename: {original_filename}")
    print(f"   Original hash: {original_hash}")
    print(f"   Protected hash: {protected_hash}")
    
    # Save hashes (this happens in the protect endpoint)
    success_original = hash_gen.save_hash_to_file(original_filename, original_hash, "original")
    success_protected = hash_gen.save_hash_to_file(original_filename, protected_hash, "protected")
    
    print(f"   Original hash saved: {success_original}")
    print(f"   Protected hash saved: {success_protected}")
    
    # Test various filename scenarios that users might upload for verification
    print("\n2. TESTING VERIFICATION WITH VARIOUS FILENAME SCENARIOS")
    
    test_scenarios = [
        {
            "name": "Exact match",
            "filename": "important_document.pdf",
            "expected": "should find hash"
        },
        {
            "name": "Different case",
            "filename": "IMPORTANT_DOCUMENT.PDF",
            "expected": "should find hash (case-insensitive)"
        },
        {
            "name": "Browser upload prefix",
            "filename": "uploaded_important_document.pdf",
            "expected": "should find hash (prefix removal)"
        },
        {
            "name": "Copy suffix",
            "filename": "important_document_copy.pdf",
            "expected": "should find hash (suffix removal)"
        },
        {
            "name": "Protected suffix",
            "filename": "important_document_protected.pdf",
            "expected": "should find hash (suffix removal)"
        },
        {
            "name": "Different extension",
            "filename": "important_document.txt",
            "expected": "should find hash (extension ignored)"
        },
        {
            "name": "No extension",
            "filename": "important_document",
            "expected": "should find hash (no extension)"
        },
        {
            "name": "Completely different name",
            "filename": "my_renamed_file.pdf",
            "expected": "should NOT find hash"
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\n   Testing: {scenario['name']}")
        print(f"   Filename: '{scenario['filename']}'")
        print(f"   Expected: {scenario['expected']}")
        
        # This is what happens in the verify endpoint
        stored_hash = hash_gen.load_hash_from_file(scenario['filename'], hash_type="protected")
        
        if stored_hash:
            print(f"   ✅ SUCCESS: Found stored hash: {stored_hash}")
            results.append({
                "scenario": scenario['name'],
                "filename": scenario['filename'],
                "result": "SUCCESS",
                "hash_found": True,
                "hash_value": stored_hash
            })
        else:
            print(f"   ❌ FAILED: No stored hash found")
            results.append({
                "scenario": scenario['name'],
                "filename": scenario['filename'],
                "result": "FAILED",
                "hash_found": False,
                "hash_value": None
            })
    
    # Summary
    print("\n3. TEST RESULTS SUMMARY")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for result in results:
        status = "✅ PASS" if result['hash_found'] else "❌ FAIL"
        print(f"{status} {result['scenario']}: '{result['filename']}'")
        if result['hash_found']:
            successful += 1
        else:
            failed += 1
    
    print(f"\nTotal: {successful} successful, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Web verification hash lookup is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Some filename variations are not being handled.")
    
    # Test the actual hash files
    print("\n4. VERIFYING HASH FILES")
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    expected_hash_file = f"{base_name}_protected.hash.json"
    expected_hash_path = os.path.join(hash_gen.hash_dir, expected_hash_file)
    
    print(f"   Expected hash file: {expected_hash_file}")
    print(f"   Hash file exists: {os.path.exists(expected_hash_path)}")
    
    if os.path.exists(expected_hash_path):
        with open(expected_hash_path, 'r') as f:
            import json
            hash_data = json.load(f)
            print(f"   Hash file content: {hash_data}")
    
    return results

if __name__ == "__main__":
    test_web_verification_fix() 