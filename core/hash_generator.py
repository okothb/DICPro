"""
Document Integrity Protection System - Hash Generator Module
Provides SHA-256 hashing functionality for document integrity verification.
"""

import hashlib
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import csv
import openpyxl


class HashGenerator:
    """
    Handles SHA-256 hash generation for documents and data integrity verification.
    Enhanced with support for both original and protected document hashes with file persistence.
    """

    def __init__(self, buffer_size: int = 65536, hash_dir: str = None):
        """
        Initialize HashGenerator.
        """
        self.buffer_size = buffer_size
        self.supported_formats = {'.txt', '.pdf', '.docx', '.jpg', '.png'}
        self.hash_dir = hash_dir or os.path.join("data", "hash")
        os.makedirs(self.hash_dir, exist_ok=True)
        self.hashes = {'original': None, 'protected': None, 'current': None}

    def generate_file_hash(self, file_path: str) -> Optional[str]:
        """
        Generate SHA-256 hash for a file, with special handling for Excel files.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            sha256_hash = hashlib.sha256()
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".xlsx", ".xls"]:
                # Hash all cell values as text
                wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                for ws in wb.worksheets:
                    for row in ws.iter_rows(values_only=True):
                        for cell in row:
                            if cell is not None:
                                sha256_hash.update(str(cell).encode("utf-8"))
                wb.close()
                return sha256_hash.hexdigest()
            elif ext == ".csv":
                with open(file_path, "r", encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        sha256_hash.update(",".join(row).encode("utf-8"))
                return sha256_hash.hexdigest()
            else:
                with open(file_path, "rb") as file:
                    while chunk := file.read(self.buffer_size):
                        sha256_hash.update(chunk)
                return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error generating hash for {file_path}: {str(e)}")
            return None

    def save_hash_to_file(self, file_path: str, hash_value: str, hash_type: str = "original") -> bool:
        """
        Save hash to hash folder with metadata.
        """
        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            hash_filename = f"{base_name}_{hash_type}.hash.json"
            hash_file_path = os.path.join(self.hash_dir, hash_filename)

            hash_data = {
                'hash': hash_value, 'file_path': file_path, 'hash_type': hash_type,
                'created_at': datetime.now().isoformat(),
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            with open(hash_file_path, 'w') as f:
                json.dump(hash_data, f, indent=2)
            print(f"Hash saved: {hash_file_path}")
            return True
        except Exception as e:
            print(f"Error saving hash to file: {str(e)}")
            return False

    def load_hash_from_file(self, file_path: str, hash_type: str = "protected") -> Optional[str]:
        """
        Load hash from hash folder.
        """
        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            hash_filename = f"{base_name}_{hash_type}.hash.json"
            hash_file_path = os.path.join(self.hash_dir, hash_filename)

            if not os.path.exists(hash_file_path):
                print(f"Hash file not found: {hash_file_path}")
                return None

            with open(hash_file_path, 'r') as f:
                hash_data = json.load(f)
            return hash_data.get('hash')
        except Exception as e:
            print(f"Error loading hash from file: {str(e)}")
            return None

    def store_original_hash(self, file_path: str) -> Optional[str]:
        original_hash = self.generate_file_hash(file_path)
        if original_hash:
            self.hashes['original'] = original_hash
            self.save_hash_to_file(file_path, original_hash, "original")
        return original_hash

    def store_protected_hash(self, protected_file_path: str) -> Optional[str]:
        protected_hash = self.generate_file_hash(protected_file_path)
        if protected_hash:
            self.hashes['protected'] = protected_hash
            self.save_hash_to_file(protected_file_path, protected_hash, "protected")
        return protected_hash

    def verify_document_integrity(self, file_path: str, use_stored_hash: bool = True) -> Dict[str, Any]:
        """
        Verify document integrity using its corresponding stored hash file.
        """
        try:
            current_hash = self.generate_file_hash(file_path)
            if not current_hash:
                return {'verified': False, 'error': 'Could not generate current hash'}

            self.hashes['current'] = current_hash

            expected_hash = self.load_hash_from_file(file_path, "protected") if use_stored_hash else self.hashes['protected']
            if not expected_hash:
                return {'verified': False, 'error': 'No stored/protected hash found for verification'}

            is_verified = current_hash.lower() == expected_hash.lower()
            return {
                'verified': is_verified, 'file_path': file_path,
                'current_hash': current_hash, 'expected_hash': expected_hash
            }
        except Exception as e:
            return {'verified': False, 'error': f'Verification failed: {str(e)}'}

    def verify_integrity_against_expected(self, file_path: str, expected_hash: str) -> bool:
        """
        FIXED: Renamed from verify_file_integrity to avoid conflict.
        Verifies file integrity by comparing with an explicitly provided hash.
        """
        current_hash = self.generate_file_hash(file_path)
        if current_hash is None:
            return False
        self.hashes['current'] = current_hash
        return current_hash.lower() == expected_hash.lower()

    def generate_batch_hashes(self, file_paths: List[str]) -> Dict[str, str]:
        """
        Generate hashes for multiple files.
        """
        return {fp: self.generate_file_hash(fp) for fp in file_paths if self.generate_file_hash(fp)}

    def create_hash_manifest(self, directory_path: str, output_file: str) -> bool:
        """
        Create a manifest file containing hashes of all files in a directory.
        """
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return False

        manifest = {
            "created_at": datetime.now().isoformat(),
            "directory": directory_path, "files": {}
        }
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                hash_value = self.generate_file_hash(file_path)
                if hash_value:
                    manifest["files"][os.path.relpath(file_path, directory_path)] = hash_value
        try:
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving manifest: {str(e)}")
            return False