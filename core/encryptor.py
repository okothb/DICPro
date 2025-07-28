"""
Document Integrity Protection System - Encryption Module
Provides AES encryption/decryption functionality for secure document protection.
"""

import os
import json
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
import secrets
import base64


class DocumentEncryptor:
    """
    Handles AES encryption and decryption for document protection.
    """
    
    def __init__(self):
        """Initialize the DocumentEncryptor with default settings."""
        self.key_length = 32  # 256-bit key
        self.iv_length = 16   # 128-bit IV for AES
        self.salt_length = 16 # 128-bit salt for key derivation
        self.iterations = 100000  # PBKDF2 iterations
        self.backend = default_backend()
    
    def generate_key(self) -> bytes:
        """
        Generate a random 256-bit encryption key.
        
        Returns:
            bytes: Random 256-bit key
        """
        return secrets.token_bytes(self.key_length)
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password (str): Password to derive key from
            salt (bytes, optional): Salt for key derivation
            
        Returns:
            Tuple[bytes, bytes]: (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(self.salt_length)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_length,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def encrypt_data(self, data: bytes, key: bytes) -> Dict[str, Any]:
        """
        Encrypt data using AES-256-CBC.
        
        Args:
            data (bytes): Data to encrypt
            key (bytes): 256-bit encryption key
            
        Returns:
            Dict[str, Any]: Dictionary containing encrypted data and metadata
        """
        try:
            # Generate random IV
            iv = secrets.token_bytes(self.iv_length)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            encryptor = cipher.encryptor()
            
            # Apply PKCS7 padding
            padder = PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # Encrypt data
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            return {
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'iv': base64.b64encode(iv).decode('utf-8'),
                'timestamp': datetime.now().isoformat(),
                'algorithm': 'AES-256-CBC',
                'padding': 'PKCS7',
                'success': True
            }
            
        except Exception as e:
            return {
                'error': f"Encryption failed: {str(e)}",
                'success': False
            }
    
    def decrypt_data(self, encrypted_info: Dict[str, Any], key: bytes) -> Optional[bytes]:
        """
        Decrypt data using AES-256-CBC.
        
        Args:
            encrypted_info (Dict[str, Any]): Dictionary containing encrypted data and metadata
            key (bytes): 256-bit decryption key
            
        Returns:
            Optional[bytes]: Decrypted data or None if decryption fails
        """
        try:
            # Extract encrypted data and IV
            encrypted_data = base64.b64decode(encrypted_info['encrypted_data'].encode('utf-8'))
            iv = base64.b64decode(encrypted_info['iv'].encode('utf-8'))
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Remove PKCS7 padding
            unpadder = PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data
            
        except Exception as e:
            print(f"Decryption failed: {str(e)}")
            return None
    
    def encrypt_file(self, input_file: str, output_file: str, password: str = None, key: bytes = None) -> Dict[str, Any]:
        """
        Encrypt a file using AES-256-CBC.
        
        Args:
            input_file (str): Path to input file
            output_file (str): Path to output encrypted file
            password (str, optional): Password for key derivation
            key (bytes, optional): Direct encryption key
            
        Returns:
            Dict[str, Any]: Encryption result with metadata
        """
        try:
            if not os.path.exists(input_file):
                return {'error': 'Input file not found', 'success': False}
            
            # Generate or derive key
            if key is None:
                if password is None:
                    return {'error': 'Either password or key must be provided', 'success': False}
                key, salt = self.derive_key_from_password(password)
            else:
                salt = None
            
            # Read input file
            with open(input_file, 'rb') as f:
                file_data = f.read()
            
            # Encrypt data
            encryption_result = self.encrypt_data(file_data, key)
            if not encryption_result['success']:
                return encryption_result
            
            # Prepare output data
            output_data = {
                'file_info': {
                    'original_name': os.path.basename(input_file),
                    'original_size': len(file_data),
                    'encrypted_at': datetime.now().isoformat()
                },
                'encryption_info': encryption_result,
                'key_derivation': {
                    'method': 'PBKDF2-HMAC-SHA256' if password else 'Direct',
                    'salt': base64.b64encode(salt).decode('utf-8') if salt else None,
                    'iterations': self.iterations if password else None
                }
            }
            
            # Write encrypted file
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'original_size': len(file_data),
                'encrypted_size': os.path.getsize(output_file),
                'encryption_method': 'AES-256-CBC'
            }
            
        except Exception as e:
            return {'error': f"File encryption failed: {str(e)}", 'success': False}
    
    def decrypt_file(self, input_file: str, output_file: str, password: str = None, key: bytes = None) -> Dict[str, Any]:
        """
        Decrypt a file encrypted with encrypt_file.
        
        Args:
            input_file (str): Path to encrypted file
            output_file (str): Path to output decrypted file
            password (str, optional): Password for key derivation
            key (bytes, optional): Direct decryption key
            
        Returns:
            Dict[str, Any]: Decryption result with metadata
        """
        try:
            if not os.path.exists(input_file):
                return {'error': 'Encrypted file not found', 'success': False}
            
            # Read encrypted file
            with open(input_file, 'r') as f:
                encrypted_data = json.load(f)
            
            # Derive key if password provided
            if key is None:
                if password is None:
                    return {'error': 'Either password or key must be provided', 'success': False}
                
                salt_b64 = encrypted_data['key_derivation'].get('salt')
                if not salt_b64:
                    return {'error': 'No salt found in encrypted file', 'success': False}
                
                salt = base64.b64decode(salt_b64.encode('utf-8'))
                key, _ = self.derive_key_from_password(password, salt)
            
            # Decrypt data
            decrypted_data = self.decrypt_data(encrypted_data['encryption_info'], key)
            if decrypted_data is None:
                return {'error': 'Decryption failed - invalid key or corrupted data', 'success': False}
            
            # Write decrypted file
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
            
            return {
                'success': True,
                'input_file': input_file,
                'output_file': output_file,
                'original_name': encrypted_data['file_info']['original_name'],
                'decrypted_size': len(decrypted_data),
                'encryption_method': encrypted_data['encryption_info']['algorithm']
            }
            
        except Exception as e:
            return {'error': f"File decryption failed: {str(e)}", 'success': False}
    
    def encrypt_string(self, text: str, password: str) -> Dict[str, Any]:
        """
        Encrypt a string using password-based encryption.
        
        Args:
            text (str): Text to encrypt
            password (str): Password for encryption
            
        Returns:
            Dict[str, Any]: Encrypted text with metadata
        """
        try:
            # Derive key from password
            key, salt = self.derive_key_from_password(password)
            
            # Encrypt text
            encryption_result = self.encrypt_data(text.encode('utf-8'), key)
            if not encryption_result['success']:
                return encryption_result
            
            # Add salt to result
            encryption_result['salt'] = base64.b64encode(salt).decode('utf-8')
            encryption_result['key_derivation'] = 'PBKDF2-HMAC-SHA256'
            
            return encryption_result
            
        except Exception as e:
            return {'error': f"String encryption failed: {str(e)}", 'success': False}
    
    def decrypt_string(self, encrypted_info: Dict[str, Any], password: str) -> Optional[str]:
        """
        Decrypt a string encrypted with encrypt_string.
        
        Args:
            encrypted_info (Dict[str, Any]): Encrypted string data
            password (str): Password for decryption
            
        Returns:
            Optional[str]: Decrypted string or None if decryption fails
        """
        try:
            # Extract salt and derive key
            salt = base64.b64decode(encrypted_info['salt'].encode('utf-8'))
            key, _ = self.derive_key_from_password(password, salt)
            
            # Decrypt data
            decrypted_bytes = self.decrypt_data(encrypted_info, key)
            if decrypted_bytes is None:
                return None
            
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"String decryption failed: {str(e)}")
            return None
    
    def generate_key_file(self, output_path: str, password: str = None) -> Dict[str, Any]:
        """
        Generate and save an encryption key to file.
        
        Args:
            output_path (str): Path to save key file
            password (str, optional): Password to encrypt the key file
            
        Returns:
            Dict[str, Any]: Key generation result
        """
        try:
            # Generate random key
            key = self.generate_key()
            
            key_data = {
                'key': base64.b64encode(key).decode('utf-8'),
                'created_at': datetime.now().isoformat(),
                'key_length': self.key_length * 8,  # in bits
                'algorithm': 'AES-256'
            }
            
            # Encrypt key file if password provided
            if password:
                encrypted_key = self.encrypt_string(json.dumps(key_data), password)
                if encrypted_key['success']:
                    with open(output_path, 'w') as f:
                        json.dump(encrypted_key, f, indent=2)
                else:
                    return encrypted_key
            else:
                with open(output_path, 'w') as f:
                    json.dump(key_data, f, indent=2)
            
            return {
                'success': True,
                'key_file': output_path,
                'key_length': self.key_length * 8,
                'protected': password is not None
            }
            
        except Exception as e:
            return {'error': f"Key generation failed: {str(e)}", 'success': False}
    
    def load_key_file(self, key_file: str, password: str = None) -> Optional[bytes]:
        """
        Load encryption key from file.
        
        Args:
            key_file (str): Path to key file
            password (str, optional): Password if key file is encrypted
            
        Returns:
            Optional[bytes]: Loaded key or None if loading fails
        """
        try:
            if not os.path.exists(key_file):
                print(f"Key file not found: {key_file}")
                return None
            
            with open(key_file, 'r') as f:
                key_data = json.load(f)
            
            # Check if key file is encrypted
            if 'encrypted_data' in key_data:
                if password is None:
                    print("Key file is encrypted but no password provided")
                    return None
                
                decrypted_json = self.decrypt_string(key_data, password)
                if decrypted_json is None:
                    print("Failed to decrypt key file")
                    return None
                
                key_data = json.loads(decrypted_json)
            
            # Extract and decode key
            key_b64 = key_data.get('key')
            if not key_b64:
                print("No key found in key file")
                return None
            
            return base64.b64decode(key_b64.encode('utf-8'))
            
        except Exception as e:
            print(f"Failed to load key file: {str(e)}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # Initialize encryptor
    encryptor = DocumentEncryptor()
    
    # Example 1: String encryption/decryption
    print("=== String Encryption Example ===")
    test_text = "This is a confidential document that needs protection."
    password = "secure_password_123"
    
    encrypted_result = encryptor.encrypt_string(test_text, password)
    if encrypted_result['success']:
        print("Text encrypted successfully")
        
        decrypted_text = encryptor.decrypt_string(encrypted_result, password)
        print(f"Decrypted text: {decrypted_text}")
        print(f"Match: {test_text == decrypted_text}")
    
    # Example 2: File encryption/decryption
    print("\n=== File Encryption Example ===")
    
    # Create test file
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document for encryption.")
    
    # Encrypt file
    encrypted_file = "test_document.encrypted"
    encrypt_result = encryptor.encrypt_file(test_file, encrypted_file, password=password)
    
    if encrypt_result['success']:
        print("File encrypted successfully")
        print(f"Original size: {encrypt_result['original_size']} bytes")
        print(f"Encrypted size: {encrypt_result['encrypted_size']} bytes")
        
        # Decrypt file
        decrypted_file = "test_document_decrypted.txt"
        decrypt_result = encryptor.decrypt_file(encrypted_file, decrypted_file, password=password)
        
        if decrypt_result['success']:
            print("File decrypted successfully")
            
            # Verify content
            with open(decrypted_file, 'r') as f:
                decrypted_content = f.read()
            
            with open(test_file, 'r') as f:
                original_content = f.read()
            
            print(f"Content match: {original_content == decrypted_content}")
    
    # Example 3: Key file generation
    print("\n=== Key File Example ===")
    key_file = "encryption.key"
    key_result = encryptor.generate_key_file(key_file, password="key_password")
    
    if key_result['success']:
        print("Key file generated successfully")
        
        # Load key
        loaded_key = encryptor.load_key_file(key_file, password="key_password")
        if loaded_key:
            print(f"Key loaded successfully, length: {len(loaded_key)} bytes")
    
    # Clean up test files
    test_files = [test_file, encrypted_file, decrypted_file, key_file]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nTest completed - files cleaned up")
