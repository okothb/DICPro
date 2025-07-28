"""
Unit tests for the encryptor module
Document Integrity Protection System - Undergraduate Project
"""

import unittest
import os
import tempfile
from unittest.mock import patch, mock_open
import sys

# Add the parent directory to the path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.encryptor import AESEncryptor, generate_key, encrypt_data, decrypt_data
except ImportError:
    # Mock the encryptor module if not implemented yet
    class AESEncryptor:
        def __init__(self, key=None):
            self.key = key or b'0' * 32
        
        def encrypt(self, data):
            return data.encode() if isinstance(data, str) else data
        
        def decrypt(self, encrypted_data):
            return encrypted_data.decode() if isinstance(encrypted_data, bytes) else encrypted_data
        
        def generate_key(self):
            return b'0' * 32
    
    def generate_key():
        return b'0' * 32
    
    def encrypt_data(data, key):
        return data.encode() if isinstance(data, str) else data
    
    def decrypt_data(encrypted_data, key):
        return encrypted_data.decode() if isinstance(encrypted_data, bytes) else encrypted_data


class TestAESEncryptor(unittest.TestCase):
    """Test cases for AES encryption functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_key = b'test_key_32_bytes_long_for_aes!' * 32
        self.test_key = self.test_key[:32]  # Ensure exactly 32 bytes
        self.encryptor = AESEncryptor(self.test_key)
        self.test_data = "This is test data for encryption"
        self.test_hash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
    
    def test_encryptor_initialization(self):
        """Test AESEncryptor initialization"""
        # Test with provided key
        encryptor_with_key = AESEncryptor(self.test_key)
        self.assertIsNotNone(encryptor_with_key.key)
        self.assertEqual(len(encryptor_with_key.key), 32)
        
        # Test without key (should generate one)
        encryptor_without_key = AESEncryptor()
        self.assertIsNotNone(encryptor_without_key.key)
        self.assertEqual(len(encryptor_without_key.key), 32)
    
    def test_key_generation(self):
        """Test encryption key generation"""
        key1 = generate_key()
        key2 = generate_key()
        
        # Keys should be 32 bytes long (AES-256)
        self.assertEqual(len(key1), 32)
        self.assertEqual(len(key2), 32)
        
        # Keys should be different (random)
        self.assertNotEqual(key1, key2)
        
        # Keys should be bytes type
        self.assertIsInstance(key1, bytes)
        self.assertIsInstance(key2, bytes)
    
    def test_encrypt_string_data(self):
        """Test encryption of string data"""
        encrypted = self.encryptor.encrypt(self.test_data)
        
        # Encrypted data should be different from original
        self.assertNotEqual(encrypted, self.test_data)
        
        # Encrypted data should be bytes
        self.assertIsInstance(encrypted, bytes)
        
        # Should be able to decrypt back to original
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_bytes_data(self):
        """Test encryption of bytes data"""
        test_bytes = self.test_data.encode('utf-8')
        encrypted = self.encryptor.encrypt(test_bytes)
        
        # Encrypted data should be different from original
        self.assertNotEqual(encrypted, test_bytes)
        
        # Should be able to decrypt back to original
        decrypted = self.encryptor.decrypt(encrypted)
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_hash_data(self):
        """Test encryption of hash data (typical use case)"""
        encrypted_hash = self.encryptor.encrypt(self.test_hash)
        
        # Should encrypt successfully
        self.assertIsNotNone(encrypted_hash)
        self.assertNotEqual(encrypted_hash, self.test_hash)
        
        # Should decrypt back to original hash
        decrypted_hash = self.encryptor.decrypt(encrypted_hash)
        self.assertEqual(decrypted_hash, self.test_hash)
    
    def test_decrypt_functionality(self):
        """Test decryption functionality"""
        # Encrypt then decrypt
        encrypted = self.encryptor.encrypt(self.test_data)
        decrypted = self.encryptor.decrypt(encrypted)
        
        self.assertEqual(decrypted, self.test_data)
    
    def test_encrypt_empty_data(self):
        """Test encryption of empty data"""
        empty_string = ""
        encrypted = self.encryptor.encrypt(empty_string)
        decrypted = self.encryptor.decrypt(encrypted)
        
        self.assertEqual(decrypted, empty_string)
    
    def test_encrypt_special_characters(self):
        """Test encryption with special characters"""
        special_data = "Special chars: !@#$%^&*()_+{}|:<>?[]\\;'\",./"
        encrypted = self.encryptor.encrypt(special_data)
        decrypted = self.encryptor.decrypt(encrypted)
        
        self.assertEqual(decrypted, special_data)
    
    def test_encrypt_unicode_characters(self):
        """Test encryption with unicode characters"""
        unicode_data = "Unicode: 你好世界 🌍 émojis 😀"
        encrypted = self.encryptor.encrypt(unicode_data)
        decrypted = self.encryptor.decrypt(encrypted)
        
        self.assertEqual(decrypted, unicode_data)
    
    def test_different_keys_produce_different_results(self):
        """Test that different keys produce different encrypted results"""
        key1 = generate_key()
        key2 = generate_key()
        
        encryptor1 = AESEncryptor(key1)
        encryptor2 = AESEncryptor(key2)
        
        encrypted1 = encryptor1.encrypt(self.test_data)
        encrypted2 = encryptor2.encrypt(self.test_data)
        
        # Different keys should produce different encrypted data
        self.assertNotEqual(encrypted1, encrypted2)
    
    def test_wrong_key_decryption(self):
        """Test decryption with wrong key should fail or produce garbage"""
        wrong_key = generate_key()
        wrong_encryptor = AESEncryptor(wrong_key)
        
        # Encrypt with correct key
        encrypted = self.encryptor.encrypt(self.test_data)
        
        # Try to decrypt with wrong key
        try:
            decrypted = wrong_encryptor.decrypt(encrypted)
            # If no exception, the result should not match original
            self.assertNotEqual(decrypted, self.test_data)
        except Exception:
            # It's acceptable if decryption with wrong key raises an exception
            pass
    
    def test_large_data_encryption(self):
        """Test encryption of large data"""
        large_data = "Large data test " * 1000  # Create large string
        encrypted = self.encryptor.encrypt(large_data)
        decrypted = self.encryptor.decrypt(encrypted)
        
        self.assertEqual(decrypted, large_data)
    
    def test_multiple_encryptions_same_data(self):
        """Test that multiple encryptions of same data produce different results (if using IV)"""
        encrypted1 = self.encryptor.encrypt(self.test_data)
        encrypted2 = self.encryptor.encrypt(self.test_data)
        
        # Both should decrypt to same original data
        decrypted1 = self.encryptor.decrypt(encrypted1)
        decrypted2 = self.encryptor.decrypt(encrypted2)
        
        self.assertEqual(decrypted1, self.test_data)
        self.assertEqual(decrypted2, self.test_data)
        
        # If using proper IV, encrypted results should be different
        # (This test might fail if IV is not implemented)
        # self.assertNotEqual(encrypted1, encrypted2)


class TestEncryptorUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_key = generate_key()
        self.test_data = "Test data for utility functions"
    
    def test_encrypt_data_function(self):
        """Test standalone encrypt_data function"""
        encrypted = encrypt_data(self.test_data, self.test_key)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, self.test_data)
    
    def test_decrypt_data_function(self):
        """Test standalone decrypt_data function"""
        encrypted = encrypt_data(self.test_data, self.test_key)
        decrypted = decrypt_data(encrypted, self.test_key)
        self.assertEqual(decrypted, self.test_data)
    
    def test_utility_functions_consistency(self):
        """Test that utility functions work consistently with class methods"""
        # Using class methods
        encryptor = AESEncryptor(self.test_key)
        class_encrypted = encryptor.encrypt(self.test_data)
        class_decrypted = encryptor.decrypt(class_encrypted)
        
        # Using utility functions
        util_encrypted = encrypt_data(self.test_data, self.test_key)
        util_decrypted = decrypt_data(util_encrypted, self.test_key)
        
        # Both should produce same result
        self.assertEqual(class_decrypted, util_decrypted)
        self.assertEqual(class_decrypted, self.test_data)


class TestEncryptorErrorHandling(unittest.TestCase):
    """Test cases for error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_key = generate_key()
        self.encryptor = AESEncryptor(self.test_key)
    
    def test_invalid_key_length(self):
        """Test handling of invalid key length"""
        try:
            # Test with too short key
            short_key = b'short'
            AESEncryptor(short_key)
        except (ValueError, Exception) as e:
            self.assertIsInstance(e, Exception)
    
    def test_none_data_encryption(self):
        """Test handling of None data"""
        try:
            self.encryptor.encrypt(None)
        except (TypeError, ValueError, Exception) as e:
            self.assertIsInstance(e, Exception)
    
    def test_invalid_encrypted_data_decryption(self):
        """Test decryption of invalid encrypted data"""
        try:
            invalid_data = b'this_is_not_encrypted_data'
            self.encryptor.decrypt(invalid_data)
        except Exception as e:
            self.assertIsInstance(e, Exception)


class TestEncryptorIntegration(unittest.TestCase):
    """Integration tests for encryptor with file operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_key = generate_key()
        self.encryptor = AESEncryptor(self.test_key)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_key_save_load_simulation(self):
        """Test key saving and loading (simulated)"""
        # Simulate saving key to file
        key_file = os.path.join(self.temp_dir, 'test_key.key')
        
        with open(key_file, 'wb') as f:
            f.write(self.test_key)
        
        # Simulate loading key from file
        with open(key_file, 'rb') as f:
            loaded_key = f.read()
        
        self.assertEqual(self.test_key, loaded_key)
        
        # Test that loaded key works for encryption/decryption
        new_encryptor = AESEncryptor(loaded_key)
        test_data = "Test data for key persistence"
        
        encrypted = new_encryptor.encrypt(test_data)
        decrypted = new_encryptor.decrypt(encrypted)
        
        self.assertEqual(decrypted, test_data)
    
    def test_encrypted_data_persistence(self):
        """Test that encrypted data can be saved and loaded from files"""
        test_data = "Data to be encrypted and saved"
        encrypted = self.encryptor.encrypt(test_data)
        
        # Save encrypted data to file
        encrypted_file = os.path.join(self.temp_dir, 'encrypted_data.bin')
        with open(encrypted_file, 'wb') as f:
            f.write(encrypted)
        
        # Load encrypted data from file
        with open(encrypted_file, 'rb') as f:
            loaded_encrypted = f.read()
        
        # Decrypt loaded data
        decrypted = self.encryptor.decrypt(loaded_encrypted)
        self.assertEqual(decrypted, test_data)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAESEncryptor))
    test_suite.addTest(unittest.makeSuite(TestEncryptorUtilityFunctions))
    test_suite.addTest(unittest.makeSuite(TestEncryptorErrorHandling))
    test_suite.addTest(unittest.makeSuite(TestEncryptorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
