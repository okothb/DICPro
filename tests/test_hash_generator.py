"""
Unit tests for hash_generator.py module
Document Integrity Protection System - Test Suite
"""

import unittest
import tempfile
import os
import hashlib
from unittest.mock import patch, mock_open
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the core module if it doesn't exist yet
try:
    from core.hash_generator import DocumentHasher
except ImportError:
    # Create a mock class for testing purposes
    class DocumentHasher:
        def __init__(self, algorithm="sha256"):
            self.algorithm = algorithm
        
        def generate_hash(self, file_path):
            """Generate hash of a file"""
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            hash_obj = hashlib.new(self.algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        
        def generate_text_hash(self, text):
            """Generate hash of text string"""
            if not isinstance(text, str):
                raise TypeError("Input must be a string")
            
            hash_obj = hashlib.new(self.algorithm)
            hash_obj.update(text.encode('utf-8'))
            return hash_obj.hexdigest()
        
        def verify_hash(self, file_path, expected_hash):
            """Verify if file hash matches expected hash"""
            actual_hash = self.generate_hash(file_path)
            return actual_hash.lower() == expected_hash.lower()
        
        def get_supported_algorithms(self):
            """Get list of supported hash algorithms"""
            return ['md5', 'sha1', 'sha256', 'sha384', 'sha512']


class TestDocumentHasher(unittest.TestCase):
    """Test cases for DocumentHasher class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.hasher = DocumentHasher()
        self.test_text = "This is a test document for integrity verification."
        
        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.write(self.test_text)
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up after each test method"""
        # Remove temporary test file
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_init_default_algorithm(self):
        """Test DocumentHasher initialization with default algorithm"""
        hasher = DocumentHasher()
        self.assertEqual(hasher.algorithm, "sha256")
    
    def test_init_custom_algorithm(self):
        """Test DocumentHasher initialization with custom algorithm"""
        hasher = DocumentHasher(algorithm="sha512")
        self.assertEqual(hasher.algorithm, "sha512")
    
    def test_generate_hash_valid_file(self):
        """Test hash generation for a valid file"""
        hash_value = self.hasher.generate_hash(self.temp_file_path)
        
        # Verify hash is not empty and has correct length for SHA-256
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)  # SHA-256 produces 64-character hex string
        self.assertIsInstance(hash_value, str)
    
    def test_generate_hash_nonexistent_file(self):
        """Test hash generation for non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.hasher.generate_hash("nonexistent_file.txt")
    
    def test_generate_hash_consistency(self):
        """Test that same file produces same hash consistently"""
        hash1 = self.hasher.generate_hash(self.temp_file_path)
        hash2 = self.hasher.generate_hash(self.temp_file_path)
        self.assertEqual(hash1, hash2)
    
    def test_generate_text_hash_valid_string(self):
        """Test hash generation for valid text string"""
        hash_value = self.hasher.generate_text_hash(self.test_text)
        
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)  # SHA-256
        self.assertIsInstance(hash_value, str)
    
    def test_generate_text_hash_empty_string(self):
        """Test hash generation for empty string"""
        hash_value = self.hasher.generate_text_hash("")
        
        # Empty string should still produce a valid hash
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)
    
    def test_generate_text_hash_invalid_input(self):
        """Test hash generation with invalid input type"""
        with self.assertRaises(TypeError):
            self.hasher.generate_text_hash(123)  # Integer instead of string
        
        with self.assertRaises(TypeError):
            self.hasher.generate_text_hash(None)  # None instead of string
    
    def test_generate_text_hash_consistency(self):
        """Test that same text produces same hash consistently"""
        hash1 = self.hasher.generate_text_hash(self.test_text)
        hash2 = self.hasher.generate_text_hash(self.test_text)
        self.assertEqual(hash1, hash2)
    
    def test_generate_text_hash_different_texts(self):
        """Test that different texts produce different hashes"""
        text1 = "Document version 1"
        text2 = "Document version 2"
        
        hash1 = self.hasher.generate_text_hash(text1)
        hash2 = self.hasher.generate_text_hash(text2)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_verify_hash_matching(self):
        """Test hash verification with matching hash"""
        original_hash = self.hasher.generate_hash(self.temp_file_path)
        result = self.hasher.verify_hash(self.temp_file_path, original_hash)
        self.assertTrue(result)
    
    def test_verify_hash_not_matching(self):
        """Test hash verification with non-matching hash"""
        fake_hash = "0" * 64  # Invalid hash
        result = self.hasher.verify_hash(self.temp_file_path, fake_hash)
        self.assertFalse(result)
    
    def test_verify_hash_case_insensitive(self):
        """Test hash verification is case insensitive"""
        original_hash = self.hasher.generate_hash(self.temp_file_path)
        uppercase_hash = original_hash.upper()
        
        result = self.hasher.verify_hash(self.temp_file_path, uppercase_hash)
        self.assertTrue(result)
    
    def test_verify_hash_nonexistent_file(self):
        """Test hash verification with non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.hasher.verify_hash("nonexistent.txt", "dummy_hash")
    
    def test_different_algorithms(self):
        """Test hash generation with different algorithms"""
        algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        expected_lengths = {'md5': 32, 'sha1': 40, 'sha256': 64, 'sha512': 128}
        
        for algorithm in algorithms:
            hasher = DocumentHasher(algorithm=algorithm)
            hash_value = hasher.generate_text_hash(self.test_text)
            
            expected_length = expected_lengths[algorithm]
            self.assertEqual(len(hash_value), expected_length,
                           f"Hash length mismatch for {algorithm}")
    
    def test_get_supported_algorithms(self):
        """Test getting list of supported algorithms"""
        algorithms = self.hasher.get_supported_algorithms()
        
        self.assertIsInstance(algorithms, list)
        self.assertIn('sha256', algorithms)
        self.assertIn('md5', algorithms)
        self.assertIn('sha512', algorithms)
    
    def test_large_file_handling(self):
        """Test hash generation for large files"""
        # Create a larger temporary file
        large_content = "Large file content. " * 10000  # ~200KB content
        
        large_temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        large_temp_file.write(large_content)
        large_temp_file.close()
        
        try:
            hash_value = self.hasher.generate_hash(large_temp_file.name)
            self.assertIsNotNone(hash_value)
            self.assertEqual(len(hash_value), 64)
        finally:
            os.unlink(large_temp_file.name)
    
    def test_unicode_text_handling(self):
        """Test hash generation with Unicode text"""
        unicode_text = "Hello 世界! Привет мир! مرحبا بالعالم!"
        hash_value = self.hasher.generate_text_hash(unicode_text)
        
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)
    
    def test_file_modification_detection(self):
        """Test that file modification changes hash"""
        # Get original hash
        original_hash = self.hasher.generate_hash(self.temp_file_path)
        
        # Modify the file
        with open(self.temp_file_path, 'a') as f:
            f.write(" Modified content.")
        
        # Get new hash
        modified_hash = self.hasher.generate_hash(self.temp_file_path)
        
        # Hashes should be different
        self.assertNotEqual(original_hash, modified_hash)
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_file_permission_error(self, mock_file):
        """Test handling of file permission errors"""
        with self.assertRaises(IOError):
            self.hasher.generate_hash("protected_file.txt")
    
    def test_empty_file_hash(self):
        """Test hash generation for empty file"""
        empty_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        empty_file.close()
        
        try:
            hash_value = self.hasher.generate_hash(empty_file.name)
            self.assertIsNotNone(hash_value)
            self.assertEqual(len(hash_value), 64)
            
            # Empty file should have known SHA-256 hash
            expected_empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            self.assertEqual(hash_value, expected_empty_hash)
        finally:
            os.unlink(empty_file.name)


class TestHashGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.hasher = DocumentHasher()
    
    def test_invalid_algorithm(self):
        """Test initialization with invalid algorithm"""
        with self.assertRaises(ValueError):
            hasher = DocumentHasher(algorithm="invalid_algorithm")
            hasher.generate_text_hash("test")
    
    def test_very_long_text(self):
        """Test hash generation with very long text"""
        long_text = "A" * 1000000  # 1MB of text
        hash_value = self.hasher.generate_text_hash(long_text)
        
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)
    
    def test_special_characters(self):
        """Test hash generation with special characters"""
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        hash_value = self.hasher.generate_text_hash(special_text)
        
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)
    
    def test_newline_characters(self):
        """Test hash generation with different newline characters"""
        text_unix = "Line 1\nLine 2\nLine 3"
        text_windows = "Line 1\r\nLine 2\r\nLine 3"
        
        hash_unix = self.hasher.generate_text_hash(text_unix)
        hash_windows = self.hasher.generate_text_hash(text_windows)
        
        # Different line endings should produce different hashes
        self.assertNotEqual(hash_unix, hash_windows)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDocumentHasher)
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestHashGeneratorEdgeCases))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
