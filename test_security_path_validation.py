#!/usr/bin/env python3
"""
Security test suite for path validation.
Tests various attack vectors and ensures the system is secure.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.path_validator import PathValidator, validate_folder_path, sanitize_path_for_display


class TestPathValidatorSecurity(unittest.TestCase):
    """Test security aspects of path validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = PathValidator()
        
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = os.path.join(self.temp_dir, "test_output")
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_path_traversal_attacks(self):
        """Test various path traversal attack vectors."""
        attack_vectors = [
            # Basic directory traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            
            # URL encoded traversal
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            
            # Mixed encoding
            "..%2f..%2f..%2fetc%2fpasswd",
            "%2e%2e%2f..%2f..%2fetc%2fpasswd",
            
            # Unicode traversal
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
            
            # Double encoding
            "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
            
            # Alternative separators
            "..\\..\\..\\etc\\passwd",
            "..//..//..//etc//passwd",
            
            # Null byte injection
            "..\\..\\..\\etc\\passwd\0",
            "..%00..%00..%00etc%00passwd",
        ]
        
        for attack_path in attack_vectors:
            with self.subTest(attack_path=attack_path):
                is_valid, message = validate_folder_path(attack_path)
                self.assertFalse(is_valid, f"Attack vector '{attack_path}' should be rejected")
                self.assertIn("forbidden pattern", message.lower())
    
    def test_protocol_injection_attacks(self):
        """Test protocol injection attacks."""
        attack_vectors = [
            # File protocol
            "file:///etc/passwd",
            "file://C:\\windows\\system32\\config\\sam",
            
            # HTTP/HTTPS protocols
            "http://malicious.com/script.js",
            "https://evil.com/payload.exe",
            
            # FTP protocols
            "ftp://malicious.com/file.exe",
            "ftps://evil.com/script.sh",
            
            # UNC paths
            "\\\\malicious-server\\share\\malware.exe",
            "\\\\192.168.1.100\\admin$\\system32\\cmd.exe",
            
            # Data URIs
            "data:text/html,<script>alert('xss')</script>",
            "data:application/x-javascript,alert('xss')",
        ]
        
        for attack_path in attack_vectors:
            with self.subTest(attack_path=attack_path):
                is_valid, message = validate_folder_path(attack_path)
                self.assertFalse(is_valid, f"Protocol injection '{attack_path}' should be rejected")
    
    def test_command_injection_attacks(self):
        """Test command injection attacks."""
        attack_vectors = [
            # Command separators
            "C:\\temp; rm -rf /",
            "C:\\temp & del C:\\windows",
            "C:\\temp | cat /etc/passwd",
            "C:\\temp `whoami`",
            
            # Command substitution
            "$(rm -rf /)",
            "`rm -rf /`",
            "${rm -rf /}",
            
            # PowerShell commands
            "C:\\temp; powershell -Command \"Remove-Item C:\\windows\"",
            "C:\\temp & cmd /c del C:\\windows",
        ]
        
        for attack_path in attack_vectors:
            with self.subTest(attack_path=attack_path):
                is_valid, message = validate_folder_path(attack_path)
                self.assertFalse(is_valid, f"Command injection '{attack_path}' should be rejected")
    
    def test_script_injection_attacks(self):
        """Test script injection attacks."""
        attack_vectors = [
            # JavaScript injection
            "C:\\temp<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "vbscript:msgbox('xss')",
            
            # HTML injection
            "C:\\temp<img src=x onerror=alert('xss')>",
            "C:\\temp<iframe src=javascript:alert('xss')>",
            
            # Event handlers
            "C:\\temp\" onmouseover=\"alert('xss')\"",
            "C:\\temp' onload='alert(\"xss\")'",
        ]
        
        for attack_path in attack_vectors:
            with self.subTest(attack_path=attack_path):
                is_valid, message = validate_folder_path(attack_path)
                self.assertFalse(is_valid, f"Script injection '{attack_path}' should be rejected")
    
    def test_sql_injection_attacks(self):
        """Test SQL injection attacks."""
        attack_vectors = [
            # SQL injection patterns
            "C:\\temp'; DROP TABLE users; --",
            "C:\\temp' UNION SELECT * FROM users --",
            "C:\\temp' OR 1=1 --",
            "C:\\temp' AND 1=1 --",
            
            # SQL comments
            "C:\\temp -- comment",
            "C:\\temp /* comment */",
            
            # SQL keywords
            "C:\\temp SELECT * FROM users",
            "C:\\temp INSERT INTO users VALUES",
            "C:\\temp UPDATE users SET",
            "C:\\temp DELETE FROM users",
        ]
        
        for attack_path in attack_vectors:
            with self.subTest(attack_path=attack_path):
                is_valid, message = validate_folder_path(attack_path)
                self.assertFalse(is_valid, f"SQL injection '{attack_path}' should be rejected")
    
    def test_unicode_attacks(self):
        """Test Unicode-based attacks."""
        attack_vectors = [
            # Unicode normalization attacks
            "..\\u2215..\\u2215..\\u2215etc\\u2215passwd",  # Unicode slash
            "..\\u2216..\\u2216..\\u2216etc\\u2216passwd",  # Unicode backslash
            
            # Unicode null bytes
            "C:\\temp\\u0000malicious",
            "C:\\temp\\u0000\\u0000\\u0000",
            
            # Unicode control characters
            "C:\\temp\\u0001\\u0002\\u0003",
            "C:\\temp\\u001f\\u007f\\u009f",
        ]
        
        for attack_path in attack_vectors:
            with self.subTest(attack_path=attack_path):
                is_valid, message = validate_folder_path(attack_path)
                self.assertFalse(is_valid, f"Unicode attack '{attack_path}' should be rejected")
    
    def test_safe_paths_are_accepted(self):
        """Test that legitimate safe paths are accepted."""
        # Test with the actual test directory we created
        safe_paths = [
            self.test_dir,  # Our test directory should be safe
        ]
        
        for safe_path in safe_paths:
            if os.path.exists(safe_path):
                with self.subTest(safe_path=safe_path):
                    is_valid, message = validate_folder_path(safe_path)
                    self.assertTrue(is_valid, f"Safe path '{safe_path}' should be accepted")
    
    def test_path_sanitization(self):
        """Test path sanitization for display."""
        dangerous_paths = [
            "C:\\temp<script>alert('xss')</script>",
            "C:\\temp<img src=x onerror=alert('xss')>",
            "C:\\temp\" onmouseover=\"alert('xss')\"",
            "C:\\temp<iframe src=javascript:alert('xss')>",
        ]
        
        for dangerous_path in dangerous_paths:
            with self.subTest(dangerous_path=dangerous_path):
                sanitized = sanitize_path_for_display(dangerous_path)
                self.assertNotIn("<script>", sanitized)
                self.assertNotIn("<img", sanitized)
                self.assertNotIn("<iframe", sanitized)
                self.assertNotIn("onmouseover", sanitized)
                self.assertNotIn("onerror", sanitized)
                self.assertNotIn("javascript:", sanitized)
    
    def test_path_normalization(self):
        """Test path normalization security."""
        # Test null byte removal
        path_with_nulls = "C:\\temp\0\0\0malicious"
        normalized = self.validator.normalize_path(path_with_nulls)
        self.assertNotIn("\0", normalized)
        
        # Test control character removal
        path_with_controls = "C:\\temp\x01\x02\x03malicious"
        normalized = self.validator.normalize_path(path_with_controls)
        self.assertNotIn("\x01", normalized)
        self.assertNotIn("\x02", normalized)
        self.assertNotIn("\x03", normalized)
    
    def test_symlink_protection(self):
        """Test protection against symbolic link attacks."""
        # Create a symbolic link to a sensitive directory
        sensitive_dir = "/etc" if os.name != 'nt' else "C:\\Windows\\System32"
        
        if os.path.exists(sensitive_dir):
            symlink_path = os.path.join(self.temp_dir, "malicious_link")
            try:
                os.symlink(sensitive_dir, symlink_path)
                is_valid, message = validate_folder_path(symlink_path)
                self.assertFalse(is_valid, "Symbolic links should be rejected")
                self.assertIn("Symbolic links are not allowed", message)
            except (OSError, NotImplementedError):
                # Symlinks not supported on this system
                pass
    
    def test_directory_permissions(self):
        """Test directory permission validation."""
        # Test non-existent directory
        non_existent = os.path.join(self.temp_dir, "non_existent_dir")
        is_valid, message = validate_folder_path(non_existent)
        self.assertFalse(is_valid)
        self.assertIn("does not exist", message)
        
        # Test file instead of directory
        test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        is_valid, message = validate_folder_path(test_file)
        self.assertFalse(is_valid)
        self.assertIn("not a directory", message)
    
    def test_pattern_matching_efficiency(self):
        """Test that pattern matching is efficient and doesn't cause DoS."""
        import time
        
        # Create a path that would cause catastrophic backtracking if regex is vulnerable
        long_path = "C:\\temp" + "\\" * 1000 + "malicious"
        
        start_time = time.time()
        is_valid, message = validate_folder_path(long_path)
        end_time = time.time()
        
        # Should complete quickly (less than 1 second)
        self.assertLess(end_time - start_time, 1.0)
        self.assertFalse(is_valid)


if __name__ == "__main__":
    # Run the security tests
    unittest.main(verbosity=2) 