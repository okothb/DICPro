"""
DocProject API Client Example
Demonstrates how to use the DocProject API for document protection and verification.
"""

import requests
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class DocProjectAPIClient:
    """Client for interacting with the DocProject API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def protect_document(
        self, 
        file_path: str, 
        secret_data: str, 
        encrypt_payload: bool = False, 
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Protect a single document
        
        Args:
            file_path: Path to the file to protect
            secret_data: Secret data to embed
            encrypt_payload: Whether to encrypt the payload
            password: Encryption password (required if encrypt_payload is True)
        
        Returns:
            API response with protection results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if encrypt_payload and not password:
            raise ValueError("Password required when encryption is enabled")
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            data = {
                'secret_data': secret_data,
                'encrypt_payload': encrypt_payload
            }
            if password:
                data['password'] = password
            
            response = self.session.post(f"{self.base_url}/protect", files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def verify_document(self, file_path: str) -> Dict[str, Any]:
        """
        Verify a protected document
        
        Args:
            file_path: Path to the protected file to verify
        
        Returns:
            API response with verification results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            response = self.session.post(f"{self.base_url}/verify", files=files)
            response.raise_for_status()
            return response.json()
    
    def extract_data(self, file_path: str) -> Dict[str, Any]:
        """
        Extract embedded data from a protected document
        
        Args:
            file_path: Path to the protected file
        
        Returns:
            API response with extracted data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
            response = self.session.post(f"{self.base_url}/extract", files=files)
            response.raise_for_status()
            return response.json()
    
    def batch_protect(
        self, 
        file_paths: list, 
        secret_data: str, 
        encrypt_payload: bool = False, 
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Protect multiple documents in batch
        
        Args:
            file_paths: List of file paths to protect
            secret_data: Secret data to embed
            encrypt_payload: Whether to encrypt the payload
            password: Encryption password (required if encrypt_payload is True)
        
        Returns:
            API response with batch processing results
        """
        if encrypt_payload and not password:
            raise ValueError("Password required when encryption is enabled")
        
        files = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'rb') as f:
                files.append(('files', (os.path.basename(file_path), f, 'application/octet-stream')))
        
        data = {
            'secret_data': secret_data,
            'encrypt_payload': encrypt_payload
        }
        if password:
            data['password'] = password
        
        response = self.session.post(f"{self.base_url}/batch-protect", files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    def download_file(self, file_id: str, output_path: str) -> bool:
        """
        Download a protected file by its ID
        
        Args:
            file_id: File ID from protection response
            output_path: Where to save the downloaded file
        
        Returns:
            True if download successful
        """
        response = self.session.get(f"{self.base_url}/download/{file_id}")
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files on the server"""
        response = self.session.delete(f"{self.base_url}/cleanup")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the DocProject API client"""
    
    # Initialize client
    client = DocProjectAPIClient("http://localhost:8000")
    
    try:
        # Check API health
        print("Checking API health...")
        health = client.health_check()
        print(f"API Status: {health['status']}")
        print(f"Version: {health['version']}")
        print()
        
        # Example file paths (replace with actual files)
        test_files = [
            "sample_document.pdf",
            "sample_image.png",
            "sample_spreadsheet.xlsx"
        ]
        
        # Example 1: Protect a single document
        print("=== Protecting Single Document ===")
        if os.path.exists(test_files[0]):
            result = client.protect_document(
                file_path=test_files[0],
                secret_data="This is a secret message embedded in the document",
                encrypt_payload=False
            )
            print(f"Protection Result: {result['message']}")
            print(f"Method: {result['method']}")
            print(f"Original Hash: {result['original_hash']}")
            print(f"Protected Hash: {result['protected_hash']}")
            print()
        
        # Example 2: Verify a protected document
        print("=== Verifying Protected Document ===")
        if os.path.exists(test_files[0]):
            result = client.verify_document(test_files[0])
            print(f"Verification Result: {result['message']}")
            print(f"Verified: {result['is_verified']}")
            print(f"Current Hash: {result['current_hash']}")
            print(f"Stored Hash: {result['stored_hash']}")
            if result['extracted_data']:
                print(f"Extracted Data: {result['extracted_data']}")
            print()
        
        # Example 3: Extract data from protected document
        print("=== Extracting Data ===")
        if os.path.exists(test_files[0]):
            result = client.extract_data(test_files[0])
            print(f"Extraction Result: {result['message']}")
            print(f"Extracted Data: {result['extracted_data']}")
            print(f"Hashes Match: {result['hashes_match']}")
            print()
        
        # Example 4: Batch protection
        print("=== Batch Protection ===")
        existing_files = [f for f in test_files if os.path.exists(f)]
        if existing_files:
            result = client.batch_protect(
                file_paths=existing_files,
                secret_data="Batch secret message",
                encrypt_payload=False
            )
            print(f"Batch Result: {result['message']}")
            print(f"Total Files: {result['total_files']}")
            print(f"Successful: {result['successful']}")
            print(f"Failed: {result['failed']}")
            
            for file_result in result['results']:
                print(f"  {file_result['file']}: {file_result['status']}")
            print()
        
        # Example 5: Cleanup
        print("=== Cleanup ===")
        cleanup_result = client.cleanup_temp_files()
        print(f"Cleanup: {cleanup_result['message']}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the API server is running on http://localhost:8000")
        print("Run: python api.py")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 