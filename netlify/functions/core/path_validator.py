"""
Simplified Path Validator for Netlify Functions
"""

import os
import re


def validate_folder_path(path: str) -> tuple:
    """Validate folder path for security"""
    if not path:
        return False, "Path cannot be empty"
    
    # Basic security checks
    if '..' in path or path.startswith('/'):
        return False, "Invalid path: contains dangerous characters"
    
    # For serverless, we don't actually validate filesystem paths
    # since we use temporary directories
    return True, "Path validated"


def sanitize_path_for_display(path: str) -> str:
    """Sanitize path for display"""
    if not path:
        return ""
    
    # Remove dangerous characters
    sanitized = re.sub(r'[<>:"|?*]', '_', path)
    return sanitized[:100]  # Limit length