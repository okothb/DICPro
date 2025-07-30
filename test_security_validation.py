#!/usr/bin/env python3
"""
Test script to verify security validation functionality
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.security_validator import validate_secret_data, validate_extracted_data, sanitize_secret_data

def test_security_validation():
    """Test the security validation functionality"""
    
    print("🔒 Testing Security Validation")
    print("=" * 50)
    
    # Test cases for valid data
    valid_test_cases = [
        "Hello World",
        "123456789",
        "Contact: john@example.com",
        "Phone: (555) 123-4567",
        "Address: 123 Main St, City, State 12345",
        "Meeting notes: Discuss project timeline and budget",
        "Password: MySecurePass123!",
        "Text with punctuation: commas, periods. And symbols: @#$%",
        "Multi-line\ntext\nwith\nnewlines",
        "Numbers: 1, 2, 3, 4, 5",
        "Special chars: ()[]{}<>/~",
        "A" * 1000,  # Long but valid text
    ]
    
    print("\n✅ Testing Valid Data:")
    for i, test_data in enumerate(valid_test_cases, 1):
        is_valid, error = validate_secret_data(test_data)
        status = "PASS" if is_valid else "FAIL"
        print(f"  {i:2d}. {status}: {repr(test_data[:50])}{'...' if len(test_data) > 50 else ''}")
        if not is_valid:
            print(f"       Error: {error}")
    
    # Test cases for malicious data
    malicious_test_cases = [
        ("<script>alert('xss')</script>", "Script tags"),
        ("javascript:alert('xss')", "JavaScript protocol"),
        ("data:text/html,<script>alert('xss')</script>", "Data URI with script"),
        ("cmd /c dir", "Command execution"),
        ("powershell -Command Get-Process", "PowerShell command"),
        ("exec(system('ls'))", "Function execution"),
        ("eval('alert(1)')", "Eval function"),
        ("http://malicious.com", "URL"),
        ("file:///etc/passwd", "File protocol"),
        ("\\\\server\\share", "Network path"),
        ("SELECT * FROM users", "SQL injection"),
        ("-- SQL comment", "SQL comment"),
        ("/* SQL block comment */", "SQL block comment"),
        ("onclick=alert('xss')", "Event handler"),
        ("<iframe src='malicious.com'>", "Iframe"),
        ("MZ executable header", "Executable header"),
        ("PE Windows executable", "Windows executable"),
        ("ELF Linux executable", "Linux executable"),
        ("test.exe", "Executable extension"),
        ("script.bat", "Batch file"),
        ("malware.vbs", "VBScript"),
        ("A" * 10001, "Too long text"),
        ("   \t\n   ", "Only whitespace"),
        ("", "Empty string"),
    ]
    
    print("\n❌ Testing Malicious Data:")
    for i, (test_data, description) in enumerate(malicious_test_cases, 1):
        is_valid, error = validate_secret_data(test_data)
        status = "PASS" if not is_valid else "FAIL"
        print(f"  {i:2d}. {status}: {description}")
        if is_valid:
            print(f"       Should have been rejected but was accepted")
        else:
            print(f"       Correctly rejected: {error}")
    
    # Test sanitization
    print("\n🧹 Testing Sanitization:")
    sanitize_test_cases = [
        ("Hello<script>alert('xss')</script>World", "Script in middle"),
        ("javascript:alert('xss')", "JavaScript protocol"),
        ("Normal text with <script>bad</script> content", "Mixed content"),
        ("123<script>456", "Script at end"),
        ("<script>789", "Script at start"),
    ]
    
    for i, (test_data, description) in enumerate(sanitize_test_cases, 1):
        sanitized = sanitize_secret_data(test_data)
        print(f"  {i}. {description}")
        print(f"     Original: {repr(test_data)}")
        print(f"     Sanitized: {repr(sanitized)}")
        print()
    
    # Test extracted data validation
    print("\n🔍 Testing Extracted Data Validation:")
    extracted_test_cases = [
        (b"Safe extracted data", "Safe data"),
        (b"<script>alert('xss')</script>", "Malicious script"),
        (b"javascript:alert('xss')", "JavaScript protocol"),
        (b"", "Empty data"),
    ]
    
    for i, (test_data, description) in enumerate(extracted_test_cases, 1):
        is_valid, error = validate_extracted_data(test_data)
        status = "PASS" if is_valid else "FAIL"
        print(f"  {i}. {status}: {description}")
        if not is_valid:
            print(f"     Error: {error}")
    
    print("\n" + "=" * 50)
    print("✅ Security validation tests completed!")

if __name__ == "__main__":
    test_security_validation() 