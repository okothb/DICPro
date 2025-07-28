"""
File Handler Module for Document Integrity Protection System
Handles all file operations including reading, writing, validation, and path management.
Enhanced with hash metadata storage for proper document integrity verification.
"""

import os
import shutil
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Tuple, Union, Dict
import mimetypes
from datetime import datetime


class FileHandler:
    """Handles file operations for the document integrity system."""
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize FileHandler with base directory structure.
        
        Args:
            base_path (str): Base directory for all file operations
        """
        self.base_path = Path(base_path)
        self.input_dir = self.base_path / "input"
        self.output_dir = self.base_path / "output"
        self.keys_dir = self.base_path / "keys"
        self.logs_dir = self.base_path / "logs"
        self.metadata_dir = self.base_path / "metadata"  # New: For hash metadata storage
        
        # Create directories if they don't exist
        self._create_directories()
    
    def _create_directories(self) -> None:
        """Create necessary directories for the application."""
        directories = [self.input_dir, self.output_dir, self.keys_dir, 
                      self.logs_dir, self.metadata_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def read_file(self, file_path: Union[str, Path], mode: str = 'rb') -> bytes:
        """
        Read file content.
        
        Args:
            file_path (Union[str, Path]): Path to the file
            mode (str): File open mode ('rb' for binary, 'r' for text)
            
        Returns:
            bytes: File content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be accessed
            IOError: If file can't be read
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            with open(file_path, mode) as file:
                return file.read()
                
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    def write_file(self, file_path: Union[str, Path], content: Union[bytes, str], 
                   mode: str = 'wb', create_dirs: bool = True) -> bool:
        """
        Write content to file.
        
        Args:
            file_path (Union[str, Path]): Path to write the file
            content (Union[bytes, str]): Content to write
            mode (str): File open mode ('wb' for binary, 'w' for text)
            create_dirs (bool): Whether to create parent directories
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            PermissionError: If file can't be written
            IOError: If file can't be created
        """
        try:
            file_path = Path(file_path)
            
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, mode) as file:
                file.write(content)
            
            return True
            
        except Exception as e:
            raise IOError(f"Error writing file {file_path}: {str(e)}")
    
    def copy_file(self, src_path: Union[str, Path], dst_path: Union[str, Path]) -> bool:
        """
        Copy file from source to destination.
        
        Args:
            src_path (Union[str, Path]): Source file path
            dst_path (Union[str, Path]): Destination file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            src_path = Path(src_path)
            dst_path = Path(dst_path)
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {src_path}")
            
            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            return True
            
        except Exception as e:
            raise IOError(f"Error copying file from {src_path} to {dst_path}: {str(e)}")
    
    def move_file(self, src_path: Union[str, Path], dst_path: Union[str, Path]) -> bool:
        """
        Move file from source to destination.
        
        Args:
            src_path (Union[str, Path]): Source file path
            dst_path (Union[str, Path]): Destination file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            src_path = Path(src_path)
            dst_path = Path(dst_path)
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {src_path}")
            
            # Create destination directory if it doesn't exist
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            return True
            
        except Exception as e:
            raise IOError(f"Error moving file from {src_path} to {dst_path}: {str(e)}")
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file.
        
        Args:
            file_path (Union[str, Path]): Path to the file to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            raise IOError(f"Error deleting file {file_path}: {str(e)}")
    
    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        Get file information including size, modification time, and type.
        
        Args:
            file_path (Union[str, Path]): Path to the file
            
        Returns:
            dict: File information
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'modified': stat.st_mtime,
                'extension': file_path.suffix,
                'mime_type': mime_type or 'unknown',
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir()
            }
            
        except Exception as e:
            raise IOError(f"Error getting file info for {file_path}: {str(e)}")
    
    def list_files(self, directory: Union[str, Path], pattern: str = "*", 
                   recursive: bool = False) -> List[Path]:
        """
        List files in a directory.
        
        Args:
            directory (Union[str, Path]): Directory to search
            pattern (str): File pattern to match (e.g., "*.txt", "*.pdf")
            recursive (bool): Whether to search recursively
            
        Returns:
            List[Path]: List of matching file paths
        """
        try:
            directory = Path(directory)
            
            if not directory.exists():
                return []
            
            if recursive:
                files = list(directory.rglob(pattern))
            else:
                files = list(directory.glob(pattern))
            
            # Filter to only include files (not directories)
            return [f for f in files if f.is_file()]
            
        except Exception as e:
            raise IOError(f"Error listing files in {directory}: {str(e)}")
    
    def validate_file_path(self, file_path: Union[str, Path]) -> bool:
        """
        Validate if a file path is valid and accessible.
        
        Args:
            file_path (Union[str, Path]): Path to validate
            
        Returns:
            bool: True if valid and accessible, False otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Check if path exists
            if not file_path.exists():
                return False
            
            # Check if it's a file (not a directory)
            if not file_path.is_file():
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_file_hash(self, file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """
        Calculate file hash.
        
        Args:
            file_path (Union[str, Path]): Path to the file
            algorithm (str): Hash algorithm ('md5', 'sha1', 'sha256', 'sha512')
            
        Returns:
            str: File hash in hexadecimal format
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get the hash algorithm
            hash_obj = hashlib.new(algorithm)
            
            # Read file in chunks to handle large files
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            raise IOError(f"Error calculating hash for {file_path}: {str(e)}")
    
    def store_hash_metadata(self, file_path: Union[str, Path], 
                           original_hash: str, protected_hash: str) -> bool:
        """
        Store hash metadata for a protected document.
        
        Args:
            file_path (Union[str, Path]): Path to the protected file
            original_hash (str): Hash of the original document
            protected_hash (str): Hash of the protected document
            
        Returns:
            bool: True if metadata stored successfully
        """
        try:
            file_path = Path(file_path)
            
            # Create metadata filename
            metadata_filename = f"{file_path.stem}_metadata.json"
            metadata_path = self.metadata_dir / metadata_filename
            
            # Create metadata object
            metadata = {
                'filename': file_path.name,
                'original_hash': original_hash,
                'protected_hash': protected_hash,
                'algorithm': 'sha256',
                'protection_date': datetime.now().isoformat(),
                'file_size': file_path.stat().st_size if file_path.exists() else 0
            }
            
            # Write metadata to file
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            raise IOError(f"Error storing hash metadata for {file_path}: {str(e)}")
    
    def get_hash_metadata(self, file_path: Union[str, Path]) -> Optional[Dict]:
        """
        Retrieve hash metadata for a protected document.
        
        Args:
            file_path (Union[str, Path]): Path to the protected file
            
        Returns:
            Optional[Dict]: Hash metadata if found, None otherwise
        """
        try:
            file_path = Path(file_path)
            
            # Create metadata filename
            metadata_filename = f"{file_path.stem}_metadata.json"
            metadata_path = self.metadata_dir / metadata_filename
            
            if not metadata_path.exists():
                return None
            
            # Read metadata from file
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            print(f"Warning: Error retrieving hash metadata for {file_path}: {str(e)}")
            return None
    
    def get_protected_hash(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Get the stored protected hash for a file.
        
        Args:
            file_path (Union[str, Path]): Path to the protected file
            
        Returns:
            Optional[str]: Protected hash if found, None otherwise
        """
        metadata = self.get_hash_metadata(file_path)
        if metadata:
            return metadata.get('protected_hash')
        return None
    
    def get_original_hash(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Get the stored original hash for a file.
        
        Args:
            file_path (Union[str, Path]): Path to the protected file
            
        Returns:
            Optional[str]: Original hash if found, None otherwise
        """
        metadata = self.get_hash_metadata(file_path)
        if metadata:
            return metadata.get('original_hash')
        return None
    
    def delete_hash_metadata(self, file_path: Union[str, Path]) -> bool:
        """
        Delete hash metadata for a file.
        
        Args:
            file_path (Union[str, Path]): Path to the file
            
        Returns:
            bool: True if metadata deleted successfully
        """
        try:
            file_path = Path(file_path)
            
            # Create metadata filename
            metadata_filename = f"{file_path.stem}_metadata.json"
            metadata_path = self.metadata_dir / metadata_filename
            
            if metadata_path.exists():
                metadata_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            raise IOError(f"Error deleting hash metadata for {file_path}: {str(e)}")
    
    def is_supported_file_type(self, file_path: Union[str, Path], 
                              supported_types: List[str] = None) -> bool:
        """
        Check if file type is supported.
        
        Args:
            file_path (Union[str, Path]): Path to the file
            supported_types (List[str]): List of supported extensions
            
        Returns:
            bool: True if supported, False otherwise
        """
        if supported_types is None:
            # Default supported types for document integrity system
            supported_types = ['.txt', '.pdf', '.doc', '.docx', '.jpg', '.jpeg', 
                             '.png', '.gif', '.bmp', '.tiff', '.zip', '.rar']
        
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        return extension in [ext.lower() for ext in supported_types]
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove invalid characters for Windows/Unix
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure filename is not empty
        if not filename:
            filename = 'unnamed_file'
        
        return filename
    
    def get_unique_filename(self, file_path: Union[str, Path]) -> Path:
        """
        Generate unique filename if file already exists.
        
        Args:
            file_path (Union[str, Path]): Original file path
            
        Returns:
            Path: Unique file path
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return file_path
        
        # Generate unique filename
        counter = 1
        while True:
            stem = file_path.stem
            suffix = file_path.suffix
            parent = file_path.parent
            
            new_path = parent / f"{stem}_{counter}{suffix}"
            
            if not new_path.exists():
                return new_path
            
            counter += 1
    
    def clean_directory(self, directory: Union[str, Path], max_age_days: int = 30) -> int:
        """
        Clean old files from directory.
        
        Args:
            directory (Union[str, Path]): Directory to clean
            max_age_days (int): Maximum age of files in days
            
        Returns:
            int: Number of files deleted
        """
        try:
            directory = Path(directory)
            
            if not directory.exists():
                return 0
            
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            deleted_count = 0
            
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            raise IOError(f"Error cleaning directory {directory}: {str(e)}")


# Convenience functions for common operations
def read_text_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """Read text file and return content as string."""
    handler = FileHandler()
    content = handler.read_file(file_path, 'rb')
    return content.decode(encoding)


def write_text_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Write string content to text file."""
    handler = FileHandler()
    return handler.write_file(file_path, content.encode(encoding), 'wb')


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Get file size in megabytes."""
    handler = FileHandler()
    info = handler.get_file_info(file_path)
    return info['size_mb']


if __name__ == "__main__":
    # Example usage
    handler = FileHandler()
    
    # Test file operations
    test_file = "test_file.txt"
    test_content = "This is a test file for the Document Integrity Protection System."
    
    try:
        # Write test file
        if handler.write_file(test_file, test_content.encode('utf-8'), 'wb'):
            print(f"✓ Created test file: {test_file}")
        
        # Read test file
        content = handler.read_file(test_file, 'rb')
        print(f"✓ Read test file: {content.decode('utf-8')[:50]}...")
        
        # Get file info
        info = handler.get_file_info(test_file)
        print(f"✓ File info: {info['name']}, Size: {info['size']} bytes")
        
        # Get file hash
        file_hash = handler.get_file_hash(test_file)
        print(f"✓ File hash: {file_hash[:16]}...")
        
        # Test hash metadata storage
        original_hash = handler.get_file_hash(test_file)
        protected_hash = "def456789abcdef123456789abcdef123456789abcdef123456789abcdef12"
        
        if handler.store_hash_metadata(test_file, original_hash, protected_hash):
            print(f"✓ Stored hash metadata")
        
        # Retrieve metadata
        metadata = handler.get_hash_metadata(test_file)
        if metadata:
            print(f"✓ Retrieved metadata: Original hash match = {metadata['original_hash'] == original_hash}")
        
        # Clean up
        handler.delete_file(test_file)
        handler.delete_hash_metadata(test_file)
        print(f"✓ Cleaned up test files")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
