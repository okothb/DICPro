"""
Helper functions for the Document Integrity Protection System
Provides utility functions used across the application
"""

import os
import hashlib
import secrets
import time
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict, Any
from datetime import datetime
import mimetools
import mimetypes

from config import (
    SUPPORTED_TEXT_FORMATS, SUPPORTED_IMAGE_FORMATS, 
    MAX_FILE_SIZE, HASH_ALGORITHM, KEY_SIZE
)


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        bool: True if file exists and is accessible, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and os.access(path, os.R_OK)
    except (OSError, TypeError):
        return False


def validate_file_format(file_path: Union[str, Path], file_type: str = "any") -> bool:
    """
    Validate if a file has a supported format.
    
    Args:
        file_path: Path to the file
        file_type: Type of file to validate ("text", "image", or "any")
        
    Returns:
        bool: True if format is supported, False otherwise
    """
    try:
        path = Path(file_path)
        file_extension = path.suffix.lower()
        
        if file_type == "text":
            return file_extension in SUPPORTED_TEXT_FORMATS
        elif file_type == "image":
            return file_extension in SUPPORTED_IMAGE_FORMATS
        else:  # file_type == "any"
            return file_extension in (SUPPORTED_TEXT_FORMATS + SUPPORTED_IMAGE_FORMATS)
    except (AttributeError, TypeError):
        return False


def validate_file_size(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file size is within acceptable limits.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file size is acceptable, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False
        return path.stat().st_size <= MAX_FILE_SIZE
    except (OSError, TypeError):
        return False


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get comprehensive information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        dict: Dictionary containing file information
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
            
        stat = path.stat()
        file_hash = calculate_file_hash(file_path)
        
        return {
            "name": path.name,
            "path": str(path.absolute()),
            "size": stat.st_size,
            "size_human": format_file_size(stat.st_size),
            "extension": path.suffix.lower(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "hash": file_hash,
            "mime_type": mimetypes.guess_type(str(path))[0] or "unknown",
            "is_text": path.suffix.lower() in SUPPORTED_TEXT_FORMATS,
            "is_image": path.suffix.lower() in SUPPORTED_IMAGE_FORMATS
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = HASH_ALGORITHM) -> str:
    """
    Calculate hash of a file using specified algorithm.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        str: Hexadecimal hash string
    """
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        raise RuntimeError(f"Failed to calculate file hash: {str(e)}")


def generate_secure_key(key_size: int = KEY_SIZE) -> bytes:
    """
    Generate a cryptographically secure random key.
    
    Args:
        key_size: Size of the key in bytes
        
    Returns:
        bytes: Random key
    """
    return secrets.token_bytes(key_size)


def generate_salt(salt_size: int = 16) -> bytes:
    """
    Generate a random salt for encryption.
    
    Args:
        salt_size: Size of the salt in bytes
        
    Returns:
        bytes: Random salt
    """
    return secrets.token_bytes(salt_size)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format timestamp in human-readable format.
    
    Args:
        timestamp: Unix timestamp (default: current time)
        
    Returns:
        str: Formatted timestamp string
    """
    if timestamp is None:
        timestamp = time.time()
    
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    # Characters that are invalid in filenames
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Ensure filename is not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name


def create_backup_filename(original_path: Union[str, Path]) -> Path:
    """
    Create a backup filename with timestamp.
    
    Args:
        original_path: Path to original file
        
    Returns:
        Path: Path for backup file
    """
    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"
    return path.parent / backup_name


def ensure_directory_exists(directory: Union[str, Path]) -> bool:
    """
    Ensure that a directory exists, create it if it doesn't.
    
    Args:
        directory: Path to directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def clean_temp_files(directory: Union[str, Path], max_age_hours: int = 24) -> int:
    """
    Clean temporary files older than specified age.
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age in hours
        
    Returns:
        int: Number of files cleaned
    """
    try:
        path = Path(directory)
        if not path.exists():
            return 0
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for file_path in path.glob("*.tmp"):
            try:
                if current_time - file_path.stat().st_mtime > max_age_seconds:
                    file_path.unlink()
                    cleaned_count += 1
            except (OSError, PermissionError):
                continue
                
        return cleaned_count
    except Exception:
        return 0


def validate_key_format(key_data: bytes) -> bool:
    """
    Validate if key data has the correct format and size.
    
    Args:
        key_data: Key data to validate
        
    Returns:
        bool: True if key format is valid
    """
    try:
        return isinstance(key_data, bytes) and len(key_data) == KEY_SIZE
    except (TypeError, AttributeError):
        return False


def chunks(data: Union[str, bytes], chunk_size: int):
    """
    Split data into chunks of specified size.
    
    Args:
        data: Data to split
        chunk_size: Size of each chunk
        
    Yields:
        Chunks of the specified size
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def progress_callback(current: int, total: int, callback_func=None):
    """
    Helper function for progress tracking.
    
    Args:
        current: Current progress value
        total: Total value
        callback_func: Optional callback function to call with progress
    """
    if callback_func and total > 0:
        percentage = min(100, (current * 100) // total)
        callback_func(percentage)


def binary_to_hex(data: bytes) -> str:
    """
    Convert binary data to hexadecimal string.
    
    Args:
        data: Binary data
        
    Returns:
        str: Hexadecimal representation
    """
    return data.hex().upper()


def hex_to_binary(hex_string: str) -> bytes:
    """
    Convert hexadecimal string to binary data.
    
    Args:
        hex_string: Hexadecimal string
        
    Returns:
        bytes: Binary data
    """
    try:
        return bytes.fromhex(hex_string.replace(' ', ''))
    except ValueError as e:
        raise ValueError(f"Invalid hexadecimal string: {str(e)}")


def is_text_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a text file by attempting to read it as text.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file appears to be text
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Read first 1024 bytes to check
            sample = f.read(1024)
            return True
    except (UnicodeDecodeError, IOError, OSError):
        return False