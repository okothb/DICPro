#!/usr/bin/env python3
"""
Security validation module for document protection system.
Validates secret data to ensure it only contains safe text and numbers.
"""

import re
import string
from typing import Dict, Tuple, List


class SecurityValidator:
    """Validates secret data to prevent malicious content embedding."""
    
    def __init__(self):
        # Define allowed characters: letters, numbers, spaces, and common punctuation
        self.allowed_chars = set(
            string.ascii_letters +  # a-z, A-Z
            string.digits +         # 0-9
            string.whitespace +     # spaces, tabs, newlines
            '.,!?;:()[]{}"\'-_@#$%&*+=<>/~'  # safe punctuation
        )
        
        # Patterns that indicate potentially malicious content
        self.malicious_patterns = [
            # Script tags and executable content
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'data:application/x-javascript',
            
            # Command execution patterns
            r'(cmd|powershell|bash|sh)\s+/[ck]',
            r'exec\s*\(',
            r'eval\s*\(',
            r'system\s*\(',
            
            # Network and file system access
            r'(http|https|ftp)://',
            r'file://',
            r'\\\\([a-zA-Z0-9\-\.]+)\\',
            
            # SQL injection patterns
            r'(union|select|insert|update|delete|drop|create|alter)\s+',
            r'--\s*$',  # SQL comments
            r'/\*.*?\*/',  # SQL block comments
            
            # XSS patterns
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
            
            # Malicious file content indicators (only at start of string)
            r'^MZ\s*',  # DOS executable header
            r'^PE\s*',  # Windows executable header
            r'^ELF\s*',  # Linux executable header
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                for pattern in self.malicious_patterns]
    
    def validate_secret_data(self, secret_data: str) -> Tuple[bool, str]:
        """
        Validate secret data to ensure it only contains safe content.
        
        Args:
            secret_data (str): The secret data to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not secret_data:
            return False, "Secret data cannot be empty."
        
        # Check for excessive whitespace (potential obfuscation)
        if len(secret_data.strip()) == 0:
            return False, "Secret data cannot be empty or contain only whitespace."
        
        # Check length limits
        if len(secret_data) > 10000:  # 10KB limit
            return False, "Secret data is too long. Maximum allowed length is 10,000 characters."
        
        # Check for malicious patterns
        for pattern in self.compiled_patterns:
            if pattern.search(secret_data):
                return False, f"Secret data contains potentially malicious content: {pattern.pattern}"
        
        # Check for disallowed characters
        disallowed_chars = set(secret_data) - self.allowed_chars
        if disallowed_chars:
            return False, f"Secret data contains disallowed characters: {''.join(sorted(disallowed_chars))}"
        
        return True, ""
    
    def sanitize_secret_data(self, secret_data: str) -> str:
        """
        Sanitize secret data by removing potentially dangerous content.
        
        Args:
            secret_data (str): The secret data to sanitize
            
        Returns:
            str: Sanitized secret data
        """
        if not secret_data:
            return ""
        
        # Remove malicious patterns
        sanitized = secret_data
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub('', sanitized)
        
        # Remove disallowed characters
        sanitized = ''.join(char for char in sanitized if char in self.allowed_chars)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def validate_extracted_data(self, extracted_data: bytes) -> Tuple[bool, str]:
        """
        Validate extracted data to ensure it's safe before returning to user.
        
        Args:
            extracted_data (bytes): The extracted data to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Try to decode as UTF-8
            decoded_data = extracted_data.decode('utf-8', errors='ignore')
            
            # Validate the decoded data
            return self.validate_secret_data(decoded_data)
            
        except Exception as e:
            return False, f"Failed to validate extracted data: {str(e)}"
    
    def get_validation_rules(self) -> Dict[str, str]:
        """
        Get the validation rules for display to users.
        
        Returns:
            Dict[str, str]: Validation rules
        """
        return {
            "allowed_chars": "Letters (a-z, A-Z), numbers (0-9), spaces, and common punctuation",
            "max_length": "10,000 characters",
            "prohibited": "Scripts, executables, commands, URLs, SQL, XSS, and other malicious content",
            "examples": "Text messages, numbers, simple documents, contact information"
        }


# Global validator instance
security_validator = SecurityValidator()


def validate_secret_data(secret_data: str) -> Tuple[bool, str]:
    """Convenience function to validate secret data."""
    return security_validator.validate_secret_data(secret_data)


def sanitize_secret_data(secret_data: str) -> str:
    """Convenience function to sanitize secret data."""
    return security_validator.sanitize_secret_data(secret_data)


def validate_extracted_data(extracted_data: bytes) -> Tuple[bool, str]:
    """Convenience function to validate extracted data."""
    return security_validator.validate_extracted_data(extracted_data) 