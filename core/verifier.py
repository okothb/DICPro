"""
Document Integrity Verification Module
Part of Document Integrity Protection System

This module provides comprehensive document integrity verification
using SHA-256 hashing and digital signatures.
"""

import os
import json
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import logging

# Import the DocumentSteganography module
from core.steganography import DocumentSteganography

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentVerifier:
    """
    Main class for document integrity verification.
    Handles hash verification, digital signatures, and integrity reports.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the Document Verifier.

        Args:
            data_dir (str): Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.hash_dir = self.data_dir / "hash"
        self.reports_dir = self.data_dir / "reports"
        self.keys_dir = self.data_dir / "keys"

        # Create directories if they don't exist
        self._create_directories()

        # Supported hash algorithms
        self.supported_algorithms = ['sha256', 'sha512', 'md5', 'sha1']
        self.default_algorithm = 'sha256'

        # Initialize Steganography module
        self.steganography = DocumentSteganography()

    def _create_directories(self) -> None:
        """Create necessary directories for the verifier."""
        directories = [self.hash_dir, self.reports_dir, self.keys_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def _get_hash_file_path(self, file_path: str, is_protected: bool = False) -> Path:
        """
        Generates a consistent path for the hash metadata file based on the original document's name.
        If is_protected is True, strips '_protected' from the stem to get the original file's stem.
        Raises ValueError if file_path is None.
        """
        if file_path is None:
            raise ValueError("file_path cannot be None for _get_hash_file_path")
        base_filename = Path(file_path).stem
        if is_protected and base_filename.endswith('_protected'):
            base_filename = base_filename[:-10]  # Remove '_protected'
        return self.hash_dir / f"{base_filename}.hash.json"

    def calculate_file_hash(self, file_path: str, algorithm: str = None) -> str:
        """
        Calculate hash of a file using specified algorithm.

        Args:
            file_path (str): Path to the file
            algorithm (str): Hash algorithm to use (default: sha256)

        Returns:
            str: Hexadecimal hash string

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If algorithm is not supported
        """
        if file_path is None:
            raise ValueError("file_path cannot be None for calculate_file_hash")
        if algorithm is None:
            algorithm = self.default_algorithm

        if algorithm not in self.supported_algorithms:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        hash_func = hashlib.new(algorithm)
        chunk_size = 8192
        try:
            with open(file_path, 'rb') as file:
                while chunk := file.read(chunk_size):
                    hash_func.update(chunk)
            file_hash = hash_func.hexdigest()
            logger.info(f"Calculated {algorithm} hash for {file_path}: {file_hash[:16]}...")
            return file_hash
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {str(e)}")
            raise

    def store_document_hashes(self, original_file_path: str, protected_file_path: str) -> bool:
        """
        FIXED: Calculate and store hashes for both original and protected documents
        in a single, unified JSON file. This is the primary function to save hash data.

        Args:
            original_file_path (str): Path to the original document
            protected_file_path (str): Path to the protected document

        Returns:
            bool: True if both hashes are stored successfully
        """
        try:
            original_hash = self.calculate_file_hash(original_file_path)
            protected_hash = self.calculate_file_hash(protected_file_path)

            if not (original_hash and protected_hash):
                logger.error("Hash calculation failed for one or both files.")
                return False

            hash_file_path = self._get_hash_file_path(original_file_path)

            hash_data = {
                'file_name': Path(original_file_path).name,
                'last_updated': datetime.now().isoformat(),
                'hashes': {
                    'original': {
                        'hash_value': original_hash,
                        'algorithm': self.default_algorithm,
                        'file_path': str(Path(original_file_path).resolve()),
                        'stored_date': datetime.now().isoformat()
                    },
                    'protected': {
                        'hash_value': protected_hash,
                        'algorithm': self.default_algorithm,
                        'file_path': str(Path(protected_file_path).resolve()),
                        'stored_date': datetime.now().isoformat()
                    }
                }
            }

            with open(hash_file_path, 'w') as f:
                json.dump(hash_data, f, indent=4)
            logger.info(f"Successfully stored original and protected hashes to {hash_file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to store document hashes: {str(e)}")
            return False

    def retrieve_hash(self, file_path: str, hash_type: str) -> Optional[str]:
        """
        Retrieve a stored hash (original or protected) for a file from the unified JSON hash file.
        Uses the correct hash file path for both original and protected files.
        """
        if file_path is None:
            logger.warning("retrieve_hash called with file_path=None")
            return None
        # If looking for a protected hash, assume file_path may be the protected file
        is_protected = (hash_type == 'protected')
        hash_file_path = self._get_hash_file_path(file_path, is_protected=is_protected)

        if not hash_file_path.exists():
            logger.warning(f"No hash file found at {hash_file_path}. Cannot retrieve hash.")
            return None

        try:
            with open(hash_file_path, 'r') as f:
                hash_data = json.load(f)

            retrieved_hash = hash_data.get('hashes', {}).get(hash_type, {}).get('hash_value')
            if retrieved_hash:
                logger.info(f"Successfully retrieved '{hash_type}' hash for {Path(file_path).name}.")
            else:
                logger.warning(f"'{hash_type}' hash not found within {hash_file_path}.")

            return retrieved_hash

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error reading or parsing hash file {hash_file_path}: {str(e)}")
            return None

    def verify_protected_document(self, protected_file_path: str) -> Dict[str, Union[bool, str]]:
        """
        FIXED: Verifies the integrity of a protected document by comparing its current hash
        against the securely stored protected hash.

        Args:
            protected_file_path (str): Path to the protected document.

        Returns:
            Dict[str, Union[bool, str]]: Verification result.
        """
        try:
            # 1. Retrieve the stored protected hash. The file is identified by its base name.
            stored_protected_hash = self.retrieve_hash(protected_file_path, 'protected')

            if not stored_protected_hash:
                return {
                    'is_valid': False,
                    'message': 'No stored protected hash found for this document. Cannot verify integrity.',
                    'status': 'FAILED',
                    'hash_type_used': 'None'
                }

            # 2. Calculate the current hash of the protected file
            current_file_hash = self.calculate_file_hash(protected_file_path)

            # 3. Compare the hashes
            if current_file_hash == stored_protected_hash:
                return {
                    'is_valid': True,
                    'message': 'Protected document integrity verified against stored hash. Document is AUTHENTIC.',
                    'status': 'AUTHENTIC',
                    'hash_type_used': 'Protected (stored)'
                }
            else:
                return {
                    'is_valid': False,
                    'message': 'Protected document has been tampered with. Current hash does not match stored protected hash.',
                    'status': 'TAMPERED',
                    'hash_type_used': 'Protected (stored)'
                }

        except FileNotFoundError:
            return {'is_valid': False, 'message': f'Protected file not found: {protected_file_path}', 'status': 'FAILED', 'hash_type_used': 'None'}
        except Exception as e:
            logger.error(f"Error verifying protected document {protected_file_path}: {str(e)}")
            return {'is_valid': False, 'message': f'An unexpected error occurred during verification: {str(e)}', 'status': 'FAILED', 'hash_type_used': 'None'}

    def batch_verify(self, file_paths: List[str], use_protected_hash: bool = True) -> Dict[str, Any]:
        """
        Perform batch verification for multiple files.
        """
        results = []
        authentic_count, tampered_count, failed_count = 0, 0, 0

        for file_path in file_paths:
            if use_protected_hash:
                verification_outcome = self.verify_protected_document(file_path)
            else:
                # Verify against the original hash
                stored_hash = self.retrieve_hash(file_path, 'original')
                if stored_hash:
                    verification_outcome = self.verify_file_integrity(file_path, stored_hash)
                    verification_outcome['message'] = f"Verified against stored original hash: {verification_outcome['message']}"
                else:
                    verification_outcome = {'status': 'FAILED', 'message': 'No original hash found in storage.'}

            file_result = {'file': file_path, **verification_outcome}
            results.append(file_result)

            if file_result['status'] == 'AUTHENTIC': authentic_count += 1
            elif file_result['status'] == 'TAMPERED': tampered_count += 1
            else: failed_count += 1

        return {
            'summary': {
                'total_files': len(file_paths),
                'authentic_files': authentic_count,
                'tampered_files': tampered_count,
                'failed_files': failed_count
            },
            'detailed_results': results
        }

    def verify_file_integrity(self, file_path: str, expected_hash: str,
                              algorithm: str = None) -> Dict[str, Union[bool, str]]:
        """
        Verify the integrity of a file against an expected hash.
        """
        try:
            calculated_hash = self.calculate_file_hash(file_path, algorithm)
            if calculated_hash == expected_hash:
                return {'is_valid': True, 'message': 'File integrity is intact.', 'status': 'AUTHENTIC'}
            else:
                return {'is_valid': False, 'message': 'File has been tampered with or corrupted.', 'status': 'TAMPERED'}
        except FileNotFoundError:
            return {'is_valid': False, 'message': f'File not found: {file_path}', 'status': 'FAILED'}
        except Exception as e:
            return {'is_valid': False, 'message': f'An unexpected error occurred: {str(e)}', 'status': 'FAILED'}

    # ... (The rest of the methods like generate_integrity_report, get_hash_info_from_file, generate_signature, verify_signature can remain, but should be updated to use the new `retrieve_hash` method where applicable)

    def generate_integrity_report(self, file_path: str, report_type: str = 'full',
                                  output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates an integrity report for a given file.
        """
        report = {
            'file_path': file_path,
            'report_generated_at': datetime.now().isoformat(),
            'status': 'UNKNOWN',
            'messages': [],
            'hashes': {}
        }

        try:
            current_hash = self.calculate_file_hash(file_path)
            report['hashes']['current_file_hash'] = current_hash

            # Retrieve stored hashes using the new mechanism
            stored_protected_hash = self.retrieve_hash(file_path, 'protected')
            stored_original_hash = self.retrieve_hash(file_path, 'original')

            if stored_protected_hash:
                report['hashes']['stored_protected_hash'] = stored_protected_hash
                if current_hash == stored_protected_hash:
                    report['status'] = 'AUTHENTIC'
                    report['messages'].append("Current file hash matches the stored protected hash.")
                else:
                    report['status'] = 'TAMPERED'
                    report['messages'].append("WARNING: Current file hash DOES NOT match the stored protected hash.")

            if stored_original_hash:
                report['hashes']['stored_original_hash'] = stored_original_hash
                if current_hash == stored_original_hash and report['status'] != 'AUTHENTIC':
                     report['messages'].append("Info: Current hash matches the stored original hash. This may be expected if the file is unprotected.")

            if report['status'] == 'UNKNOWN':
                if not stored_original_hash and not stored_protected_hash:
                    report['messages'].append("No stored hashes (original or protected) found for comparison.")
                    report['status'] = 'UNVERIFIABLE'
                else:
                    report['status'] = 'INCONCLUSIVE'

            # Save full report to file
            if output_dir:
                report_file_name = f"{Path(file_path).stem}_integrity_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                report_path = Path(output_dir) / report_file_name
                with open(report_path, 'w') as f:
                    json.dump(report, f, indent=2)
                report['saved_to'] = str(report_path)

            return report

        except FileNotFoundError:
            return {'status': 'FAILED', 'messages': [f"File not found: {file_path}"]}
        except Exception as e:
            logger.error(f"Error generating integrity report for {file_path}: {str(e)}")
            return {'status': 'ERROR', 'messages': [f"An error occurred: {str(e)}"]}

    def generate_signature(self, file_path: str, private_key: bytes) -> Optional[str]:
        """
        Generates a digital signature for a file using HMAC-SHA256.
        """
        try:
            file_hash = self.calculate_file_hash(file_path, algorithm='sha256')
            if not file_hash:
                return None

            signer = hmac.new(private_key, file_hash.encode('utf-8'), hashlib.sha256)
            return signer.hexdigest()
        except Exception as e:
            logger.error(f"Error generating signature for {file_path}: {str(e)}")
            return None

    def verify_signature(self, file_path: str, signature: str, public_key: bytes) -> bool:
        """
        Verifies a digital signature for a file using HMAC-SHA256.
        """
        try:
            file_hash = self.calculate_file_hash(file_path, algorithm='sha256')
            if not file_hash:
                return False

            expected_signer = hmac.new(public_key, file_hash.encode('utf-8'), hashlib.sha256)

            return hmac.compare_digest(expected_signer.hexdigest(), signature)
        except Exception as e:
            logger.error(f"Error verifying signature for {file_path}: {str(e)}")
            return False

# get_hash_info_from_file is omitted as it relates to steganography, which is outside the scope of the primary fix.
# It can be added back if needed, but the core verification now relies on the robust file-based hash storage.