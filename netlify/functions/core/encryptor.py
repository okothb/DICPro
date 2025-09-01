"""
Simplified Document Encryptor for Netlify Functions
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class DocumentEncryptor:
    """Simplified encryptor for serverless environment"""
    
    def __init__(self):
        pass
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_string(self, text: str, password: str) -> dict:
        """Encrypt string with password"""
        try:
            salt = hashlib.sha256(password.encode()).digest()[:16]
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            encrypted_data = fernet.encrypt(text.encode())
            
            return {
                'success': True,
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'salt': base64.b64encode(salt).decode()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def decrypt_string(self, encrypted_data: dict, password: str) -> str:
        """Decrypt string with password"""
        try:
            salt = base64.b64decode(encrypted_data.get('salt', ''))
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            encrypted_bytes = base64.b64decode(encrypted_data.get('encrypted_data', ''))
            decrypted_data = fernet.decrypt(encrypted_bytes)
            
            return decrypted_data.decode()
        except Exception:
            return None