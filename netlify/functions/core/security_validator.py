"""
Simplified Security Validator for Netlify Functions
"""

import re


def validate_secret_data(data: str) -> tuple:
    """Validate secret data for security"""
    if not data:
        return True, None
    
    if len(data) > 10000:
        return False, "Secret data too long (max 10,000 characters)"
    
    # Check for malicious patterns
    forbidden_patterns = [
        r'<script[\s\S]*?>[\s\S]*?</script>',
        r'\b(onerror|onload)\s*=',
        r'\b(eval|exec|document\.cookie)\b',
        r'\b(powershell|cmd\.exe|bash|sh)\b',
        r'(javascript:|vbscript:|data:text/html)'
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, data, re.IGNORECASE):
            return False, "Secret data contains potentially malicious content"
    
    return True, None


def validate_extracted_data(data: bytes) -> tuple:
    """Validate extracted data for security"""
    if not data:
        return True, None
    
    try:
        text = data.decode('utf-8', errors='ignore')
        return validate_secret_data(text)
    except Exception:
        return True, None  # If can't decode, assume it's binary data