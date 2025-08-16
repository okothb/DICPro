#!/usr/bin/env python3
"""
Updated path validation using the same logic as the original path_validator.py
but with debugging output and the same robust security measures.
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
        print(f"DEBUG: normalize_path called with: '{path}'")
        
        if not path or not isinstance(path, str):
            print(f"DEBUG: Invalid input in normalize_path")
            return ""
        
        # Remove null bytes and control characters
        path = ''.join(char for char in path if ord(char) >= 32)
        print(f"DEBUG: After removing control chars: '{path}'")
        
        # Normalize unicode
        path = unicodedata.normalize('NFC', path)
        print(f"DEBUG: After unicode normalization: '{path}'")
        
        # Remove leading/trailing whitespace
        path = path.strip()
        print(f"DEBUG: After strip: '{path}'")
        
        # Convert to absolute path if relative
        if not os.path.isabs(path):
            path = os.path.abspath(path)
            print(f"DEBUG: Converted to absolute: '{path}'")
        
        return path
    
    def validate_folder_path(self, folder_path: str) -> Tuple[bool, str]:
        """
        Validate a folder path for security and accessibility.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        print(f"DEBUG: validate_folder_path called with: '{folder_path}' (type: {type(folder_path)})")
        
        try:
            if not folder_path or not isinstance(folder_path, str):
                print(f"DEBUG: Invalid or empty path provided")
                return False, "Invalid or empty path provided."
            
            # Check for forbidden patterns BEFORE normalization
            print(f"DEBUG: Checking forbidden patterns...")
            for pattern in self.compiled_patterns:
                if pattern.search(folder_path):
                    print(f"DEBUG: Found forbidden pattern: {pattern.pattern}")
                    return False, f"Path contains forbidden pattern: {pattern.pattern}"
            
            print(f"DEBUG: No forbidden patterns found")
            
            # Normalize the path
            normalized_path = self.normalize_path(folder_path)
            
            if not normalized_path:
                print(f"DEBUG: Path became empty after normalization")
                return False, "Invalid or empty path provided."
            
            # Convert to Path object for further validation
            try:
                path_obj = Path(normalized_path)
                print(f"DEBUG: Created Path object: {path_obj}")
            except Exception as e:
                print(f"DEBUG: Failed to create Path object: {e}")
                return False, f"Invalid path format: {str(e)}"
            
            # Check if path is within safe directories or is a temporary directory
            print(f"DEBUG: Checking if path is safe...")
            if not self._is_path_safe(path_obj):
                print(f"DEBUG: Path is not safe")
                return False, "Path is outside of allowed directories."
            
            print(f"DEBUG: Path is within safe directories")
            
            # Check if directory exists, create if it doesn't
            if not path_obj.exists():
                print(f"DEBUG: Directory doesn't exist, attempting to create...")
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    print(f"DEBUG: Directory created successfully")
                except PermissionError as e:
                    print(f"DEBUG: Permission error creating directory: {e}")
                    return False, f"Permission denied creating directory: {str(e)}"
                except Exception as e:
                    print(f"DEBUG: Error creating directory: {e}")
                    return False, f"Cannot create directory: {str(e)}"
            else:
                print(f"DEBUG: Directory already exists")
            
            if not path_obj.is_dir():
                print(f"DEBUG: Path is not a directory")
                return False, "Path is not a directory."
            
            # Check if directory is writable
            print(f"DEBUG: Checking write access...")
            if not os.access(str(path_obj), os.W_OK):
                print(f"DEBUG: Directory is not writable (os.access check)")
                return False, "Directory is not writable."
            
            # Additional write test
            try:
                test_file = path_obj / "test_write_access.tmp"
                test_file.write_text("test")
                test_file.unlink()  # Delete test file
                print(f"DEBUG: Write access confirmed via test file")
            except Exception as e:
                print(f"DEBUG: Write test failed: {e}")
                return False, f"Directory is not writable: {str(e)}"
            
            # Check for symbolic links (potential security risk)
            if path_obj.is_symlink():
                print(f"DEBUG: Path is a symbolic link")
                return False, "Symbolic links are not allowed for security reasons."
            
            print(f"DEBUG: All validation checks passed!")
            return True, f"Path is valid and secure: {path_obj}"
            
        except Exception as e:
            print(f"DEBUG: Unexpected error in validate_folder_path: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Path validation error: {str(e)}"
    
    def _is_path_safe(self, path_obj: Path) -> bool:
        """Check if path is within safe base directories or is a temporary directory."""
        print(f"DEBUG: _is_path_safe called with: {path_obj}")
        
        try:
            # Resolve any symbolic links
            resolved_path = path_obj.resolve()
            print(f"DEBUG: Resolved path: {resolved_path}")
            
            # Check if it's a temporary directory (for testing purposes)
            temp_dir = Path(tempfile.gettempdir())
            print(f"DEBUG: Temp directory: {temp_dir}")
            try:
                resolved_path.relative_to(temp_dir)
                print(f"DEBUG: Path is within temp directory - allowed")
                return True
            except ValueError:
                print(f"DEBUG: Path is not in temp directory")
                pass
            
            # Check if the path is within any safe base directory
            print(f"DEBUG: Checking against safe base directories: {self.safe_base_dirs}")
            for safe_dir in self.safe_base_dirs:
                safe_path = Path(safe_dir).resolve()
                print(f"DEBUG: Checking against safe dir: {safe_path}")
                try:
                    # Check if resolved_path is a subdirectory of safe_path
                    relative = resolved_path.relative_to(safe_path)
                    print(f"DEBUG: Path is within safe directory {safe_path} (relative: {relative})")
                    return True
                except ValueError:
                    # Path is not a subdirectory of this safe directory
                    print(f"DEBUG: Path is not within {safe_path}")
                    continue
            
            print(f"DEBUG: Path is not within any safe directory")
            return False
            
        except Exception as e:
            print(f"DEBUG: Error in _is_path_safe: {e}")
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


def sanitize_path(path: str) -> str:
    """Simple path sanitization for compatibility."""
    if not path:
        return ""
    
    # Just normalize separators and return
    if platform.system().lower() == 'windows':
        return path.replace('/', '\\')
    else:
        return path.replace('\\', '/')


# Test function
def test_paths():
    """Test common paths"""
    test_paths = [
        "/tmp/test_output",
        "C:/temp/test_output", 
        "C:\\temp\\test_output",
        "./test_output",
        "~/Documents/test_output",
        "~/Desktop/test_output",
        "../dangerous",  # Should fail
        "/etc/test",     # Should fail on Unix
        "C:\\Windows\\test",  # Should fail on Windows
    ]
    
    print("=== TESTING UPDATED PATH VALIDATION ===")
    for test_path in test_paths:
        print(f"\n{'='*50}")
        print(f"--- Testing: '{test_path}' ---")
        valid, message = validate_folder_path(test_path)
        print(f"Result: {valid}")
        print(f"Message: {message}")
        print(f"{'='*50}")


if __name__ == "__main__":
    test_paths()