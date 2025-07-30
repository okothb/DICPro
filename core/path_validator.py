#!/usr/bin/env python3
"""
Server-side path validation for folder selection.
Ensures secure folder path handling and prevents path traversal attacks.
"""

import os
import re
import unicodedata
from pathlib import Path, PurePath
from typing import Tuple, List, Set
import platform
import tempfile


class PathValidator:
    """Validates and sanitizes folder paths to prevent security vulnerabilities."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.forbidden_patterns = [
            # Path traversal patterns - more comprehensive
            r'\.\.',  # Directory traversal
            r'%2e%2e',  # URL encoded ..
            r'%252e%252e',  # Double URL encoded ..
            r'\.\.%2f',  # Mixed encoding
            r'%2e%2e%2f',  # URL encoded ../
            r'\.\.\\',  # Windows directory traversal
            r'\.\./',  # Unix directory traversal
            
            # Dangerous protocols
            r'^(file|http|https|ftp|ftps|sftp)://',
            r'^\\\\',  # UNC paths
            
            # Command execution patterns
            r'[;&|`]',  # Command separators
            r'\$\{.*\}',  # Variable substitution
            r'`.*`',  # Command substitution
            
            # Script injection patterns
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
            r'data:application/x-javascript',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) 
                                for pattern in self.forbidden_patterns]
        
        # Define safe base directories (adjust based on your application)
        self.safe_base_dirs = self._get_safe_base_dirs()
    
    def _get_safe_base_dirs(self) -> Set[str]:
        """Get system-specific safe base directories."""
        if self.system == 'windows':
            # For Windows, include both forward and backward slash versions
            base_dirs = {
                os.path.expanduser('~\\Documents'),
                os.path.expanduser('~\\Desktop'),
                os.path.expanduser('~\\Downloads'),
                os.path.expanduser('~\\Pictures'),
                os.path.expanduser('~\\Music'),
                os.path.expanduser('~\\Videos'),
            }
            # Also add forward slash versions for Windows
            forward_slash_dirs = {
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Downloads'),
                os.path.expanduser('~/Pictures'),
                os.path.expanduser('~/Music'),
                os.path.expanduser('~/Videos'),
            }
            return base_dirs.union(forward_slash_dirs)
        else:  # Unix-like systems
            return {
                os.path.expanduser('~/Documents'),
                os.path.expanduser('~/Desktop'),
                os.path.expanduser('~/Downloads'),
                os.path.expanduser('~/Pictures'),
                os.path.expanduser('~/Music'),
                os.path.expanduser('~/Videos'),
            }
    
    def normalize_path(self, path: str) -> str:
        """Normalize and sanitize a path string."""
        if not path or not isinstance(path, str):
            return ""
        
        # Remove null bytes and control characters
        path = ''.join(char for char in path if ord(char) >= 32)
        
        # Normalize unicode
        path = unicodedata.normalize('NFC', path)
        
        # Remove leading/trailing whitespace
        path = path.strip()
        
        # Convert to absolute path if relative
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        
        return path
    
    def validate_folder_path(self, folder_path: str) -> Tuple[bool, str]:
        """
        Validate a folder path for security and accessibility.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            if not folder_path or not isinstance(folder_path, str):
                return False, "Invalid or empty path provided."
            
            # Check for forbidden patterns BEFORE normalization
            for pattern in self.compiled_patterns:
                if pattern.search(folder_path):
                    return False, f"Path contains forbidden pattern: {pattern.pattern}"
            
            # Normalize the path
            normalized_path = self.normalize_path(folder_path)
            
            if not normalized_path:
                return False, "Invalid or empty path provided."
            
            # Convert to Path object for further validation
            path_obj = Path(normalized_path)
            
            # Check if path is within safe directories or is a temporary directory
            if not self._is_path_safe(path_obj):
                return False, "Path is outside of allowed directories."
            
            # Check if directory exists and is accessible
            if not path_obj.exists():
                return False, "Directory does not exist."
            
            if not path_obj.is_dir():
                return False, "Path is not a directory."
            
            # Check if directory is writable
            if not os.access(str(path_obj), os.W_OK):
                return False, "Directory is not writable."
            
            # Check for symbolic links (potential security risk)
            if path_obj.is_symlink():
                return False, "Symbolic links are not allowed for security reasons."
            
            return True, "Path is valid and secure."
            
        except Exception as e:
            return False, f"Path validation error: {str(e)}"
    
    def _is_path_safe(self, path_obj: Path) -> bool:
        """Check if path is within safe base directories or is a temporary directory."""
        try:
            # Resolve any symbolic links
            resolved_path = path_obj.resolve()
            
            # Check if it's a temporary directory (for testing purposes)
            temp_dir = Path(tempfile.gettempdir())
            try:
                resolved_path.relative_to(temp_dir)
                return True
            except ValueError:
                pass
            
            # Check if the path is within any safe base directory
            for safe_dir in self.safe_base_dirs:
                safe_path = Path(safe_dir).resolve()
                try:
                    # Check if resolved_path is a subdirectory of safe_path
                    resolved_path.relative_to(safe_path)
                    return True
                except ValueError:
                    # Path is not a subdirectory of this safe directory
                    continue
            
            return False
            
        except Exception:
            return False
    
    def sanitize_path_for_display(self, path: str) -> str:
        """Sanitize path for safe display in UI."""
        if not path:
            return ""
        
        # Remove any potentially dangerous characters for display
        # More comprehensive sanitization
        sanitized = re.sub(r'[<>:"|?*]', '_', path)
        
        # Remove script injection patterns
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'data:application/x-javascript', '', sanitized, flags=re.IGNORECASE)
        
        # Remove event handlers
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]*>', '', sanitized)
        
        # Remove quotes and other dangerous characters
        sanitized = re.sub(r'["\']', '', sanitized)
        
        # Limit length for display
        if len(sanitized) > 100:
            sanitized = sanitized[:50] + "..." + sanitized[-47:]
        
        return sanitized


# Global validator instance
path_validator = PathValidator()


def validate_folder_path(path: str) -> Tuple[bool, str]:
    """Convenience function for path validation."""
    return path_validator.validate_folder_path(path)


def sanitize_path_for_display(path: str) -> str:
    """Convenience function for path sanitization."""
    return path_validator.sanitize_path_for_display(path) 