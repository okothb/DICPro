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
from .db import execute_query  # Import the database query executor


class HashGenerator:
    """
    Handles SHA-256 hash generation for documents and data integrity verification.
    Integrated with a persistent database for hash storage and retrieval.
    """

    def __init__(self, buffer_size: int = 65536):
        """
        Initialize HashGenerator.
        """
        self.buffer_size = buffer_size

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
                # Open with newline='' as recommended for the csv module
                with open(file_path, "r", encoding="utf-8", newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        for cell in row:
                            sha256_hash.update(str(cell).encode("utf-8"))
                return sha256_hash.hexdigest()
            else:
                with open(file_path, "rb") as file:
                    while chunk := file.read(self.buffer_size):
                        sha256_hash.update(chunk)
                return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error generating hash for {file_path}: {str(e)}")
            return None

    def save_hashes_to_db(self, original_hash: str, protected_hash: str, original_filename: str) -> bool:
        """
        Save the original and protected hashes to the database.
        """
        try:
            query = """
            INSERT INTO document_hashes (original_hash, protected_hash, original_filename)
            VALUES (%s, %s, %s)
            ON CONFLICT (protected_hash) DO NOTHING;
            """
            params = (original_hash, protected_hash, original_filename)
            execute_query(query, params)
            print(f"Hashes saved to DB for {original_filename}")
            return True
        except Exception as e:
            print(f"Error saving hashes to DB: {str(e)}")
            return False

    def verify_hash_in_db(self, current_protected_hash: str) -> Dict[str, Any]:
        """
        Verify a protected file's hash against the database.
        """
        try:
            query = "SELECT original_hash, original_filename, created_at FROM document_hashes WHERE protected_hash = %s;"
            params = (current_protected_hash,)
            result = execute_query(query, params, fetch='one')
            if result:
                return {
                    'verified': True,
                    'original_hash': result[0],
                    'original_filename': result[1],
                    'protected_at': result[2].isoformat(),
                    'message': 'Document is authentic and verified.'
                }
            return {'verified': False, 'message': 'Hash not found in database. The document may be tampered with or is not registered.'}
        except Exception as e:
            return {'verified': False, 'message': f'Database verification error: {str(e)}'}

    def verify_integrity_against_expected(self, file_path: str, expected_hash: str) -> bool:
        """
        FIXED: Renamed from verify_file_integrity to avoid conflict.
        Verifies file integrity by comparing with an explicitly provided hash.
        """
        current_hash = self.generate_file_hash(file_path)
        if current_hash is None:
            return False
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
