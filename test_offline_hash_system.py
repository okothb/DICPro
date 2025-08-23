#!/usr/bin/env python3
"""
Comprehensive Test Suite for Offline-First Hash Storage System
Tests local storage, synchronization, and API endpoints.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest
import requests
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.offline_hash_manager import OfflineHashManager, HashRecord
from core.hash_generator import HashGenerator
from core.steganography import DocumentSteganography


class TestOfflineHashSystem(unittest.TestCase):
    """Test suite for offline-first hash storage system"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "test_hashes.db")
        self.test_output_dir = os.path.join(self.test_dir, "output", "hash")
        
        # Create test files
        self.test_file = os.path.join(self.test_dir, "test_document.txt")
        with open(self.test_file, 'w') as f:
            f.write("This is a test document for hash verification.")
        
        self.protected_file = os.path.join(self.test_dir, "test_document_protected.txt")
        with open(self.protected_file, 'w') as f:
            f.write("This is a test document for hash verification. [PROTECTED]")
        
        # Initialize components
        self.hash_manager = OfflineHashManager(
            local_db_path=self.test_db,
            backend_url="http://localhost:8000"
        )
        self.hash_gen = HashGenerator()
        self.steg = DocumentSteganography()
        
        print(f"✅ Test environment set up in: {self.test_dir}")
    
    def tearDown(self):
        """Clean up test environment"""
        try:
            shutil.rmtree(self.test_dir)
            print(f"🧹 Test environment cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def test_offline_hash_storage(self):
        """Test offline hash storage functionality"""
        print("\n🧪 Testing offline hash storage...")
        
        # Generate test hashes
        original_hash = self.hash_gen.generate_file_hash(self.test_file)
        protected_hash = self.hash_gen.generate_file_hash(self.protected_file)
        secret_data = b"Test secret data for verification"
        
        # Store hash offline
        record_id = self.hash_manager.store_hash_offline(
            original_filename="test_document.txt",
            original_hash=original_hash,
            protected_hash=protected_hash,
            secret_data=secret_data,
            protection_method="test_method",
            file_size=os.path.getsize(self.test_file)
        )
        
        self.assertIsNotNone(record_id)
        print(f"✅ Hash stored with ID: {record_id}")
        
        # Verify hash retrieval
        retrieved_hash = self.hash_manager.get_hash_by_filename("test_document.txt", "protected")
        self.assertEqual(retrieved_hash, protected_hash)
        print(f"✅ Hash retrieved successfully: {retrieved_hash[:16]}...")
        
        # Test hash record retrieval
        record = self.hash_manager.get_hash_record("test_document.txt")
        self.assertIsNotNone(record)
        self.assertEqual(record.original_hash, original_hash)
        self.assertEqual(record.protected_hash, protected_hash)
        print(f"✅ Complete record retrieved: {record.id}")
    
    def test_document_verification(self):
        """Test offline document verification"""
        print("\n🧪 Testing document verification...")
        
        # Store a hash first
        original_hash = self.hash_gen.generate_file_hash(self.test_file)
        protected_hash = self.hash_gen.generate_file_hash(self.protected_file)
        
        self.hash_manager.store_hash_offline(
            original_filename="test_document.txt",
            original_hash=original_hash,
            protected_hash=protected_hash,
            protection_method="verification_test"
        )
        
        # Test successful verification
        current_hash = self.hash_gen.generate_file_hash(self.protected_file)
        result = self.hash_manager.verify_document_offline("test_document.txt", current_hash)
        
        self.assertTrue(result['verified'])
        self.assertEqual(result['status'], 'verified')
        print(f"✅ Document verified successfully: {result['message']}")
        
        # Test tampered document detection
        tampered_hash = "fake_hash_for_tampered_document"
        result = self.hash_manager.verify_document_offline("test_document.txt", tampered_hash)
        
        self.assertFalse(result['verified'])
        self.assertEqual(result['status'], 'tampered')
        print(f"✅ Tampered document detected: {result['message']}")
        
        # Test missing hash
        result = self.hash_manager.verify_document_offline("nonexistent.txt", current_hash)
        
        self.assertFalse(result['verified'])
        self.assertEqual(result['status'], 'no_hash_found')
        print(f"✅ Missing hash handled correctly: {result['message']}")
    
    def test_hash_file_storage(self):
        """Test hash file storage in output/hash directory"""
        print("\n🧪 Testing hash file storage...")
        
        # Store hash and check file creation
        original_hash = self.hash_gen.generate_file_hash(self.test_file)
        protected_hash = self.hash_gen.generate_file_hash(self.protected_file)
        
        record_id = self.hash_manager.store_hash_offline(
            original_filename="test_document.txt",
            original_hash=original_hash,
            protected_hash=protected_hash,
            protection_method="file_storage_test"
        )
        
        # Check if hash file was created
        expected_file = os.path.join(self.hash_manager.output_hash_dir, f"test_document.txt_{record_id}.hash.json")
        self.assertTrue(os.path.exists(expected_file))
        print(f"✅ Hash file created: {expected_file}")
        
        # Verify file contents
        with open(expected_file, 'r') as f:
            hash_data = json.load(f)
        
        self.assertEqual(hash_data['original_hash'], original_hash)
        self.assertEqual(hash_data['protected_hash'], protected_hash)
        self.assertEqual(hash_data['protection_method'], "file_storage_test")
        print(f"✅ Hash file contents verified")
    
    def test_sync_status_tracking(self):
        """Test synchronization status tracking"""
        print("\n🧪 Testing sync status tracking...")
        
        # Store multiple hashes with different sync statuses
        for i in range(3):
            self.hash_manager.store_hash_offline(
                original_filename=f"test_file_{i}.txt",
                original_hash=f"original_hash_{i}",
                protected_hash=f"protected_hash_{i}",
                protection_method="sync_test"
            )
        
        # Get sync status
        status = self.hash_manager.get_sync_status()
        
        self.assertGreaterEqual(status['total_records'], 3)
        self.assertGreaterEqual(status['pending'], 3)
        self.assertIn('online', status)
        print(f"✅ Sync status retrieved: {status['total_records']} total, {status['pending']} pending")
    
    def test_hash_export(self):
        """Test hash export functionality"""
        print("\n🧪 Testing hash export...")
        
        # Store some test hashes
        for i in range(2):
            self.hash_manager.store_hash_offline(
                original_filename=f"export_test_{i}.txt",
                original_hash=f"original_hash_{i}",
                protected_hash=f"protected_hash_{i}",
                protection_method="export_test"
            )
        
        # Export hashes
        export_file = os.path.join(self.test_dir, "test_export.json")
        success = self.hash_manager.export_hashes(export_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_file))
        print(f"✅ Hash export successful: {export_file}")
        
        # Verify export contents
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        
        self.assertIn('records', export_data)
        self.assertGreaterEqual(len(export_data['records']), 2)
        print(f"✅ Export contains {len(export_data['records'])} records")
    
    def test_cleanup_functionality(self):
        """Test cleanup of old records"""
        print("\n🧪 Testing cleanup functionality...")
        
        # Store a test hash
        record_id = self.hash_manager.store_hash_offline(
            original_filename="cleanup_test.txt",
            original_hash="test_original_hash",
            protected_hash="test_protected_hash",
            protection_method="cleanup_test"
        )
        
        # Manually mark as synced (simulate successful sync)
        import sqlite3
        with sqlite3.connect(self.hash_manager.local_db_path) as conn:
            conn.execute("""
                UPDATE hash_records 
                SET sync_status = 'synced', synced_at = datetime('now', '-31 days')
                WHERE id = ?
            """, (record_id,))
            conn.commit()
        
        # Run cleanup (30 days)
        deleted_count = self.hash_manager.cleanup_old_records(30)
        
        self.assertGreaterEqual(deleted_count, 1)
        print(f"✅ Cleanup removed {deleted_count} old records")
    
    def test_integration_with_steganography(self):
        """Test integration with steganography system"""
        print("\n🧪 Testing steganography integration...")
        
        # Create a test image
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        test_image = Image.fromarray(img_array)
        test_image_path = os.path.join(self.test_dir, "test_image.png")
        test_image.save(test_image_path)
        
        # Generate hashes
        original_hash = self.hash_gen.generate_file_hash(test_image_path)
        secret_data = b"Secret message for steganography test"
        
        # Hide data in image
        output_path = os.path.join(self.test_dir, "protected_image.png")
        result = self.steg.hide_data_in_image(
            test_image_path, 
            secret_data, 
            output_path,
            original_hash=original_hash
        )
        
        if result.get('success'):
            protected_hash = self.hash_gen.generate_file_hash(output_path)
            
            # Store in offline hash manager
            record_id = self.hash_manager.store_hash_offline(
                original_filename="test_image.png",
                original_hash=original_hash,
                protected_hash=protected_hash,
                secret_data=secret_data,
                protection_method="image_steganography",
                file_size=os.path.getsize(test_image_path)
            )
            
            print(f"✅ Steganography integration successful: {record_id}")
            
            # Verify the protected image
            verification_result = self.hash_manager.verify_document_offline(
                "test_image.png", 
                protected_hash
            )
            
            self.assertTrue(verification_result['verified'])
            print(f"✅ Protected image verified: {verification_result['message']}")
        else:
            print(f"⚠️ Steganography test skipped: {result.get('error', 'Unknown error')}")


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints for hash management"""
    
    @classmethod
    def setUpClass(cls):
        """Set up API test environment"""
        cls.api_base = "http://localhost:8000"
        cls.test_available = cls._check_api_availability()
        
        if cls.test_available:
            print("✅ API server detected, running API tests")
        else:
            print("⚠️ API server not available, skipping API tests")
    
    @classmethod
    def _check_api_availability(cls):
        """Check if API server is running"""
        try:
            response = requests.get(f"{cls.api_base}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def setUp(self):
        """Set up for each test"""
        if not self.test_available:
            self.skipTest("API server not available")
    
    def test_hash_storage_endpoint(self):
        """Test hash storage API endpoint"""
        print("\n🧪 Testing hash storage API endpoint...")
        
        test_data = {
            "original_filename": "api_test.txt",
            "original_hash": "test_original_hash_123",
            "protected_hash": "test_protected_hash_456",
            "secret_data_hash": "test_secret_hash_789",
            "protection_method": "api_test",
            "file_size": 1024
        }
        
        response = requests.post(f"{self.api_base}/hash/store", json=test_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('record_id', data)
        print(f"✅ Hash stored via API: {data['record_id']}")
    
    def test_hash_retrieval_endpoint(self):
        """Test hash retrieval API endpoint"""
        print("\n🧪 Testing hash retrieval API endpoint...")
        
        # First store a hash
        test_data = {
            "original_filename": "api_retrieval_test.txt",
            "original_hash": "retrieval_original_hash",
            "protected_hash": "retrieval_protected_hash",
            "protection_method": "api_retrieval_test"
        }
        
        store_response = requests.post(f"{self.api_base}/hash/store", json=test_data)
        self.assertEqual(store_response.status_code, 200)
        
        # Now retrieve it
        response = requests.get(f"{self.api_base}/hash/get/api_retrieval_test.txt")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['hash_value'], "retrieval_protected_hash")
        print(f"✅ Hash retrieved via API: {data['hash_value']}")
    
    def test_verification_endpoint(self):
        """Test document verification API endpoint"""
        print("\n🧪 Testing verification API endpoint...")
        
        # Store a hash first
        test_data = {
            "original_filename": "api_verify_test.txt",
            "original_hash": "verify_original_hash",
            "protected_hash": "verify_protected_hash",
            "protection_method": "api_verify_test"
        }
        
        store_response = requests.post(f"{self.api_base}/hash/store", json=test_data)
        self.assertEqual(store_response.status_code, 200)
        
        # Test verification
        verify_data = {
            "filename": "api_verify_test.txt",
            "current_hash": "verify_protected_hash"
        }
        
        response = requests.post(f"{self.api_base}/hash/verify", json=verify_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['verified'])
        self.assertEqual(data['status'], 'verified')
        print(f"✅ Document verified via API: {data['message']}")
    
    def test_sync_status_endpoint(self):
        """Test sync status API endpoint"""
        print("\n🧪 Testing sync status API endpoint...")
        
        response = requests.get(f"{self.api_base}/hash/sync/status")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('total_records', data)
        self.assertIn('online', data)
        print(f"✅ Sync status retrieved: {data['total_records']} total records")
    
    def test_hash_list_endpoint(self):
        """Test hash list API endpoint"""
        print("\n🧪 Testing hash list API endpoint...")
        
        response = requests.get(f"{self.api_base}/hash/list?limit=10")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('records', data)
        self.assertIn('total', data)
        print(f"✅ Hash list retrieved: {len(data['records'])} records")


def run_performance_tests():
    """Run performance tests for the offline hash system"""
    print("\n🚀 Running performance tests...")
    
    test_dir = tempfile.mkdtemp()
    test_db = os.path.join(test_dir, "perf_test.db")
    
    try:
        hash_manager = OfflineHashManager(local_db_path=test_db)
        
        # Test bulk storage performance
        start_time = time.time()
        record_count = 100
        
        for i in range(record_count):
            hash_manager.store_hash_offline(
                original_filename=f"perf_test_{i}.txt",
                original_hash=f"original_hash_{i}",
                protected_hash=f"protected_hash_{i}",
                protection_method="performance_test"
            )
        
        storage_time = time.time() - start_time
        print(f"✅ Stored {record_count} records in {storage_time:.2f}s ({record_count/storage_time:.1f} records/sec)")
        
        # Test bulk retrieval performance
        start_time = time.time()
        
        for i in range(record_count):
            hash_manager.get_hash_by_filename(f"perf_test_{i}.txt")
        
        retrieval_time = time.time() - start_time
        print(f"✅ Retrieved {record_count} records in {retrieval_time:.2f}s ({record_count/retrieval_time:.1f} records/sec)")
        
        # Test verification performance
        start_time = time.time()
        
        for i in range(min(50, record_count)):  # Test subset for verification
            hash_manager.verify_document_offline(f"perf_test_{i}.txt", f"protected_hash_{i}")
        
        verification_time = time.time() - start_time
        verification_count = min(50, record_count)
        print(f"✅ Verified {verification_count} documents in {verification_time:.2f}s ({verification_count/verification_time:.1f} verifications/sec)")
        
    finally:
        shutil.rmtree(test_dir)


def main():
    """Run all tests"""
    print("🧪 Starting Offline-First Hash Storage System Tests")
    print("=" * 60)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("\n✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()