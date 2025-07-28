"""
Unit tests for the document integrity verifier module
Tests verification of document integrity using hash comparison and steganography extraction
"""

import unittest
import tempfile
import os
import hashlib
from unittest.mock import patch, MagicMock, mock_open
import sys
import shutil

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.verifier import DocumentVerifier, VerificationResult, VerificationError
from core.hash_generator import HashGenerator
from core.encryptor import AESEncryptor
from core.steganography import TextSteganography, ImageSteganography


class TestDocumentVerifier(unittest.TestCase):
    """Test cases for DocumentVerifier class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.verifier = DocumentVerifier()
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_document.txt")
        self.test_content = "This is a test document for integrity verification."
        
        # Create test file
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
            
        # Test encryption key
        self.test_key = b'test_key_32_bytes_for_aes_encrypt'
        
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_verifier_initialization(self):
        """Test DocumentVerifier initialization"""
        verifier = DocumentVerifier()
        self.assertIsInstance(verifier.hash_generator, HashGenerator)
        self.assertIsInstance(verifier.encryptor, AESEncryptor)
        self.assertIsInstance(verifier.text_stego, TextSteganography)
        self.assertIsInstance(verifier.image_stego, ImageSteganography)
    
    def test_verify_document_integrity_success(self):
        """Test successful document integrity verification"""
        # Create original hash
        original_hash = hashlib.sha256(self.test_content.encode()).hexdigest()
        
        # Mock steganography extraction to return the correct hash
        with patch.object(self.verifier.text_stego, 'extract_data') as mock_extract:
            mock_extract.return_value = original_hash
            
            result = self.verifier.verify_document_integrity(self.test_file)
            
            self.assertIsInstance(result, VerificationResult)
            self.assertTrue(result.is_valid)
            self.assertEqual(result.original_hash, original_hash)
            self.assertEqual(result.current_hash, original_hash)
            self.assertIsNone(result.error_message)
    
    def test_verify_document_integrity_failure(self):
        """Test failed document integrity verification (document modified)"""
        # Create different hash (simulating document modification)
        original_hash = "different_hash_value"
        current_hash = hashlib.sha256(self.test_content.encode()).hexdigest()
        
        # Mock steganography extraction to return different hash
        with patch.object(self.verifier.text_stego, 'extract_data') as mock_extract:
            mock_extract.return_value = original_hash
            
            result = self.verifier.verify_document_integrity(self.test_file)
            
            self.assertIsInstance(result, VerificationResult)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.original_hash, original_hash)
            self.assertEqual(result.current_hash, current_hash)
            self.assertIsNotNone(result.error_message)
    
    def test_verify_encrypted_document_success(self):
        """Test successful verification of encrypted document"""
        # Create and encrypt original hash
        original_hash = hashlib.sha256(self.test_content.encode()).hexdigest()
        encrypted_hash = self.verifier.encryptor.encrypt(original_hash, self.test_key)
        
        # Mock steganography extraction and decryption
        with patch.object(self.verifier.text_stego, 'extract_data') as mock_extract, \
             patch.object(self.verifier.encryptor, 'decrypt') as mock_decrypt:
            
            mock_extract.return_value = encrypted_hash
            mock_decrypt.return_value = original_hash
            
            result = self.verifier.verify_encrypted_document(self.test_file, self.test_key)
            
            self.assertTrue(result.is_valid)
            self.assertEqual(result.original_hash, original_hash)
    
    def test_verify_encrypted_document_wrong_key(self):
        """Test verification failure with wrong decryption key"""
        wrong_key = b'wrong_key_32_bytes_for_aes_encryp'
        
        with patch.object(self.verifier.text_stego, 'extract_data') as mock_extract, \
             patch.object(self.verifier.encryptor, 'decrypt') as mock_decrypt:
            
            mock_extract.return_value = "encrypted_data"
            mock_decrypt.side_effect = Exception("Decryption failed")
            
            result = self.verifier.verify_encrypted_document(self.test_file, wrong_key)
            
            self.assertFalse(result.is_valid)
            self.assertIn("Decryption failed", result.error_message)
    
    def test_verify_file_not_found(self):
        """Test verification of non-existent file"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.txt")
        
        result = self.verifier.verify_document_integrity(non_existent_file)
        
        self.assertFalse(result.is_valid)
        self.assertIn("File not found", result.error_message)
    
    def test_verify_image_document(self):
        """Test verification of image document with steganography"""
        image_file = os.path.join(self.temp_dir, "test_image.png")
        
        # Create mock image file
        with open(image_file, 'wb') as f:
            f.write(b'fake_image_data')
        
        original_hash = "test_hash_from_image"
        
        with patch.object(self.verifier.image_stego, 'extract_data') as mock_extract:
            mock_extract.return_value = original_hash
            
            result = self.verifier.verify_image_document(image_file)
            
            self.assertIsInstance(result, VerificationResult)
    
    def test_extract_hidden_data_text(self):
        """Test extraction of hidden data from text document"""
        hidden_data = "hidden_hash_value"
        
        with patch.object(self.verifier.text_stego, 'extract_data') as mock_extract:
            mock_extract.return_value = hidden_data
            
            extracted = self.verifier.extract_hidden_data(self.test_file, 'text')
            
            self.assertEqual(extracted, hidden_data)
            mock_extract.assert_called_once_with(self.test_file)
    
    def test_extract_hidden_data_image(self):
        """Test extraction of hidden data from image"""
        image_file = os.path.join(self.temp_dir, "test.png")
        hidden_data = "hidden_image_hash"
        
        with open(image_file, 'wb') as f:
            f.write(b'fake_image')
        
        with patch.object(self.verifier.image_stego, 'extract_data') as mock_extract:
            mock_extract.return_value = hidden_data
            
            extracted = self.verifier.extract_hidden_data(image_file, 'image')
            
            self.assertEqual(extracted, hidden_data)
    
    def test_extract_hidden_data_unsupported_format(self):
        """Test extraction from unsupported file format"""
        with self.assertRaises(VerificationError):
            self.verifier.extract_hidden_data(self.test_file, 'unsupported')
    
    def test_batch_verify_documents(self):
        """Test batch verification of multiple documents"""
        # Create multiple test files
        files = []
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f"test_doc_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Test document {i}")
            files.append(file_path)
        
        # Mock verification results
        with patch.object(self.verifier, 'verify_document_integrity') as mock_verify:
            mock_verify.return_value = VerificationResult(
                is_valid=True,
                original_hash="test_hash",
                current_hash="test_hash"
            )
            
            results = self.verifier.batch_verify_documents(files)
            
            self.assertEqual(len(results), 3)
            self.assertEqual(mock_verify.call_count, 3)
    
    def test_generate_verification_report(self):
        """Test generation of verification report"""
        result = VerificationResult(
            is_valid=True,
            original_hash="abc123",
            current_hash="abc123",
            file_path=self.test_file
        )
        
        report = self.verifier.generate_verification_report(result)
        
        self.assertIn("Document Integrity Verification Report", report)
        self.assertIn("VALID", report)
        self.assertIn("abc123", report)
        self.assertIn(self.test_file, report)
    
    def test_save_verification_log(self):
        """Test saving verification results to log file"""
        result = VerificationResult(
            is_valid=False,
            original_hash="abc123",
            current_hash="def456",
            file_path=self.test_file,
            error_message="Document has been modified"
        )
        
        log_file = os.path.join(self.temp_dir, "verification.log")
        
        self.verifier.save_verification_log(result, log_file)
        
        self.assertTrue(os.path.exists(log_file))
        
        with open(log_file, 'r') as f:
            log_content = f.read()
            self.assertIn("INVALID", log_content)
            self.assertIn("Document has been modified", log_content)


class TestVerificationResult(unittest.TestCase):
    """Test cases for VerificationResult class"""
    
    def test_verification_result_creation(self):
        """Test creation of VerificationResult"""
        result = VerificationResult(
            is_valid=True,
            original_hash="hash1",
            current_hash="hash1",
            file_path="/path/to/file.txt"
        )
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.original_hash, "hash1")
        self.assertEqual(result.current_hash, "hash1")
        self.assertEqual(result.file_path, "/path/to/file.txt")
        self.assertIsNone(result.error_message)
    
    def test_verification_result_with_error(self):
        """Test VerificationResult with error message"""
        result = VerificationResult(
            is_valid=False,
            original_hash="hash1",
            current_hash="hash2",
            error_message="Hash mismatch detected"
        )
        
        self.assertFalse(result.is_valid)
        self.assertNotEqual(result.original_hash, result.current_hash)
        self.assertEqual(result.error_message, "Hash mismatch detected")
    
    def test_verification_result_string_representation(self):
        """Test string representation of VerificationResult"""
        result = VerificationResult(
            is_valid=True,
            original_hash="abc123",
            current_hash="abc123"
        )
        
        result_str = str(result)
        self.assertIn("VALID", result_str)
        self.assertIn("abc123", result_str)


class TestVerificationError(unittest.TestCase):
    """Test cases for VerificationError exception"""
    
    def test_verification_error_creation(self):
        """Test creation of VerificationError"""
        error_msg = "Test verification error"
        error = VerificationError(error_msg)
        
        self.assertEqual(str(error), error_msg)
    
    def test_verification_error_inheritance(self):
        """Test VerificationError inherits from Exception"""
        error = VerificationError("Test error")
        self.assertIsInstance(error, Exception)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for document verification"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.verifier = DocumentVerifier()
        
    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_verification_workflow(self):
        """Test complete end-to-end verification workflow"""
        # Create test document
        doc_path = os.path.join(self.temp_dir, "contract.txt")
        content = "Important contract document content"
        
        with open(doc_path, 'w') as f:
            f.write(content)
        
        # Mock the complete workflow
        with patch.object(self.verifier.hash_generator, 'generate_hash') as mock_hash, \
             patch.object(self.verifier.text_stego, 'extract_data') as mock_extract:
            
            document_hash = "contract_hash_value"
            mock_hash.return_value = document_hash
            mock_extract.return_value = document_hash
            
            # Verify document
            result = self.verifier.verify_document_integrity(doc_path)
            
            # Assertions
            self.assertTrue(result.is_valid)
            self.assertEqual(result.original_hash, document_hash)
            self.assertEqual(result.current_hash, document_hash)
    
    def test_tampered_document_detection(self):
        """Test detection of tampered documents"""
        # Create original document
        doc_path = os.path.join(self.temp_dir, "important_doc.txt")
        original_content = "Original important content"
        
        with open(doc_path, 'w') as f:
            f.write(original_content)
        
        # Simulate document tampering by changing content
        tampered_content = "Tampered malicious content"
        
        with patch.object(self.verifier.hash_generator, 'generate_hash') as mock_hash, \
             patch.object(self.verifier.text_stego, 'extract_data') as mock_extract:
            
            # Original hash (stored in steganography)
            original_hash = "original_document_hash"
            # Current hash (calculated from tampered content)
            current_hash = "tampered_document_hash"
            
            mock_extract.return_value = original_hash
            mock_hash.return_value = current_hash
            
            # Temporarily modify file content
            with open(doc_path, 'w') as f:
                f.write(tampered_content)
            
            result = self.verifier.verify_document_integrity(doc_path)
            
            # Should detect tampering
            self.assertFalse(result.is_valid)
            self.assertNotEqual(result.original_hash, result.current_hash)
            self.assertIn("Hash mismatch", result.error_message)


def run_verification_tests():
    """Run all verification tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestDocumentVerifier))
    test_suite.addTest(unittest.makeSuite(TestVerificationResult))
    test_suite.addTest(unittest.makeSuite(TestVerificationError))
    test_suite.addTest(unittest.makeSuite(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests when script is executed directly
    print("Running Document Verifier Tests...")
    print("=" * 50)
    
    success = run_verification_tests()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ All verification tests passed!")
    else:
        print("\n" + "=" * 50)
        print("❌ Some verification tests failed!")
        exit(1)
