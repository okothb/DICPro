#!/usr/bin/env python3
"""
Demonstration of Offline-First Hash Storage System
Shows how the system works with and without internet connectivity.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.offline_hash_manager import OfflineHashManager
from core.hash_generator import HashGenerator
from core.steganography import DocumentSteganography


def create_demo_files(demo_dir):
    """Create demo files for testing"""
    files = {}
    
    # Create a text document
    text_file = os.path.join(demo_dir, "important_document.txt")
    with open(text_file, 'w') as f:
        f.write("""
CONFIDENTIAL BUSINESS PLAN
==========================

This document contains sensitive business information that must be protected.

Key Points:
- Market analysis shows 40% growth potential
- Investment required: $2.5M
- Expected ROI: 300% over 3 years
- Launch date: Q2 2024

This document has been protected using advanced steganography techniques.
        """.strip())
    files['text'] = text_file
    
    # Create a simple image for steganography
    try:
        from PIL import Image
        import numpy as np
        
        # Create a test image
        img_array = np.random.randint(50, 200, (200, 200, 3), dtype=np.uint8)
        # Add some pattern to make it more realistic
        for i in range(0, 200, 20):
            img_array[i:i+10, :] = [100, 150, 200]
        
        test_image = Image.fromarray(img_array)
        image_file = os.path.join(demo_dir, "company_logo.png")
        test_image.save(image_file)
        files['image'] = image_file
        print(f"✅ Created demo image: {image_file}")
        
    except ImportError:
        print("⚠️ PIL not available, skipping image demo")
        files['image'] = None
    
    return files


def demonstrate_offline_protection(demo_dir, files):
    """Demonstrate document protection with offline-first hash storage"""
    print("\n" + "="*60)
    print("🔒 DOCUMENT PROTECTION DEMONSTRATION")
    print("="*60)
    
    # Initialize components
    hash_manager = OfflineHashManager(
        local_db_path=os.path.join(demo_dir, "demo_hashes.db"),
        backend_url="http://localhost:8000"  # Will work offline if server unavailable
    )
    hash_gen = HashGenerator()
    steg = DocumentSteganography()
    
    # Protect the text document
    print("\n📄 Protecting text document...")
    text_file = files['text']
    secret_data = b"CONFIDENTIAL: This document is protected by DocPro Security Suite"
    
    # Generate original hash
    original_hash = hash_gen.generate_file_hash(text_file)
    print(f"   Original hash: {original_hash[:16]}...")
    
    # Create protected version (simulate steganography)
    protected_file = os.path.join(demo_dir, "important_document_protected.txt")
    shutil.copy2(text_file, protected_file)
    
    # Add hidden marker to simulate protection
    with open(protected_file, 'a') as f:
        f.write("\n\n<!-- PROTECTED BY DOCPRO SECURITY SUITE -->")
    
    # Generate protected hash
    protected_hash = hash_gen.generate_file_hash(protected_file)
    print(f"   Protected hash: {protected_hash[:16]}...")
    
    # Store hash offline-first
    print("\n💾 Storing hash offline-first...")
    record_id = hash_manager.store_hash_offline(
        original_filename="important_document.txt",
        original_hash=original_hash,
        protected_hash=protected_hash,
        secret_data=secret_data,
        protection_method="text_steganography",
        file_size=os.path.getsize(text_file)
    )
    
    print(f"   ✅ Hash stored locally with ID: {record_id}")
    print(f"   📁 Hash file created in: output/hash/")
    
    # Show sync status
    sync_status = hash_manager.get_sync_status()
    print(f"   🔄 Sync status: {sync_status['pending']} pending, {sync_status['synced']} synced")
    print(f"   🌐 Online: {'Yes' if sync_status['online'] else 'No (working offline)'}")
    
    return record_id, protected_file, protected_hash


def demonstrate_offline_verification(hash_manager, protected_file, protected_hash):
    """Demonstrate document verification using offline storage"""
    print("\n" + "="*60)
    print("🔍 DOCUMENT VERIFICATION DEMONSTRATION")
    print("="*60)
    
    # Test 1: Verify authentic document
    print("\n✅ Test 1: Verifying authentic document...")
    result = hash_manager.verify_document_offline("important_document.txt", protected_hash)
    
    print(f"   Status: {result['status']}")
    print(f"   Verified: {'✅ YES' if result['verified'] else '❌ NO'}")
    print(f"   Message: {result['message']}")
    print(f"   Current hash: {result['current_hash'][:16]}...")
    print(f"   Stored hash: {result['stored_hash'][:16] if result['stored_hash'] else 'None'}...")
    
    # Test 2: Detect tampered document
    print("\n🚨 Test 2: Detecting tampered document...")
    
    # Simulate tampering by modifying the file
    tampered_file = protected_file + ".tampered"
    shutil.copy2(protected_file, tampered_file)
    
    with open(tampered_file, 'a') as f:
        f.write("\n\nTHIS DOCUMENT HAS BEEN TAMPERED WITH!")
    
    # Generate hash of tampered file
    hash_gen = HashGenerator()
    tampered_hash = hash_gen.generate_file_hash(tampered_file)
    
    result = hash_manager.verify_document_offline("important_document.txt", tampered_hash)
    
    print(f"   Status: {result['status']}")
    print(f"   Verified: {'✅ YES' if result['verified'] else '❌ NO (TAMPERED!)'}")
    print(f"   Message: {result['message']}")
    print(f"   Current hash: {tampered_hash[:16]}...")
    print(f"   Stored hash: {result['stored_hash'][:16] if result['stored_hash'] else 'None'}...")
    
    # Test 3: Handle missing document
    print("\n❓ Test 3: Handling unknown document...")
    fake_hash = "fake_hash_for_unknown_document"
    result = hash_manager.verify_document_offline("unknown_document.txt", fake_hash)
    
    print(f"   Status: {result['status']}")
    print(f"   Verified: {'✅ YES' if result['verified'] else '❌ NO'}")
    print(f"   Message: {result['message']}")


def demonstrate_sync_capabilities(hash_manager):
    """Demonstrate synchronization capabilities"""
    print("\n" + "="*60)
    print("🔄 SYNCHRONIZATION DEMONSTRATION")
    print("="*60)
    
    # Show current sync status
    print("\n📊 Current synchronization status:")
    status = hash_manager.get_sync_status()
    
    print(f"   Total records: {status['total_records']}")
    print(f"   Pending sync: {status['pending']}")
    print(f"   Successfully synced: {status['synced']}")
    print(f"   Failed sync: {status['failed']}")
    print(f"   Backend online: {'✅ Yes' if status['online'] else '❌ No'}")
    
    if status['online']:
        print("\n🚀 Attempting to sync pending records...")
        sync_stats = hash_manager.sync_all_pending()
        print(f"   Synced: {sync_stats['synced']}")
        print(f"   Failed: {sync_stats['failed']}")
        print(f"   Skipped: {sync_stats['skipped']}")
    else:
        print("\n📱 Working offline - records will sync when connection is restored")
        print("   This demonstrates the offline-first approach:")
        print("   • Documents can be protected without internet")
        print("   • Verification works using local storage")
        print("   • Sync happens automatically when online")


def demonstrate_hash_management(hash_manager, demo_dir):
    """Demonstrate hash management features"""
    print("\n" + "="*60)
    print("🗄️ HASH MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Add a few more test records
    print("\n📝 Adding additional test records...")
    for i in range(3):
        hash_manager.store_hash_offline(
            original_filename=f"test_document_{i}.txt",
            original_hash=f"original_hash_{i}_{'x'*40}",
            protected_hash=f"protected_hash_{i}_{'y'*40}",
            protection_method="demo_test",
            file_size=1024 * (i + 1)
        )
    
    print("   ✅ Added 3 additional test records")
    
    # Show statistics
    print("\n📈 Storage statistics:")
    status = hash_manager.get_sync_status()
    print(f"   Total records: {status['total_records']}")
    print(f"   Database size: {os.path.getsize(hash_manager.local_db_path)} bytes")
    print(f"   Hash files in output/hash: {len(os.listdir(hash_manager.output_hash_dir))}")
    
    # Export demonstration
    print("\n📤 Exporting hash records...")
    export_file = os.path.join(demo_dir, "hash_export_demo.json")
    success = hash_manager.export_hashes(export_file)
    
    if success:
        export_size = os.path.getsize(export_file)
        print(f"   ✅ Export successful: {export_file}")
        print(f"   📊 Export file size: {export_size} bytes")
        
        # Show sample of export
        import json
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        
        print(f"   📋 Contains {len(export_data['records'])} records")
        print(f"   🕒 Exported at: {export_data['exported_at']}")
    else:
        print("   ❌ Export failed")


def demonstrate_integration_benefits():
    """Show the benefits of the offline-first approach"""
    print("\n" + "="*60)
    print("🌟 OFFLINE-FIRST BENEFITS DEMONSTRATION")
    print("="*60)
    
    benefits = [
        ("🚀 Performance", "Local storage provides instant access to hash records"),
        ("📱 Offline Support", "Documents can be protected and verified without internet"),
        ("🔄 Auto-Sync", "Records automatically sync when connection is restored"),
        ("🛡️ Reliability", "System works even if backend server is unavailable"),
        ("💾 Redundancy", "Hashes stored both locally and in backend for safety"),
        ("📊 Scalability", "Local database handles thousands of records efficiently"),
        ("🔒 Security", "Sensitive hash data stored locally under user control"),
        ("🌐 Flexibility", "Works in various network conditions and environments")
    ]
    
    for title, description in benefits:
        print(f"\n{title}")
        print(f"   {description}")
    
    print(f"\n💡 Key Innovation:")
    print(f"   Traditional systems require constant internet connectivity.")
    print(f"   Our offline-first approach ensures document protection works")
    print(f"   anywhere, anytime, with seamless cloud sync when available.")


def main():
    """Run the complete demonstration"""
    print("🚀 OFFLINE-FIRST HASH STORAGE SYSTEM DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how documents can be protected and verified")
    print("using an offline-first approach with cloud synchronization.")
    
    # Create temporary demo environment
    demo_dir = tempfile.mkdtemp(prefix="docpro_demo_")
    print(f"\n📁 Demo environment: {demo_dir}")
    
    try:
        # Create demo files
        print("\n📄 Creating demo files...")
        files = create_demo_files(demo_dir)
        
        # Demonstrate protection
        record_id, protected_file, protected_hash = demonstrate_offline_protection(demo_dir, files)
        
        # Initialize hash manager for subsequent demos
        hash_manager = OfflineHashManager(
            local_db_path=os.path.join(demo_dir, "demo_hashes.db"),
            backend_url="http://localhost:8000"
        )
        
        # Demonstrate verification
        demonstrate_offline_verification(hash_manager, protected_file, protected_hash)
        
        # Demonstrate sync capabilities
        demonstrate_sync_capabilities(hash_manager)
        
        # Demonstrate hash management
        demonstrate_hash_management(hash_manager, demo_dir)
        
        # Show benefits
        demonstrate_integration_benefits()
        
        print("\n" + "="*60)
        print("✅ DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📁 Demo files preserved in: {demo_dir}")
        print("🔍 You can examine the generated files and database")
        print("🚀 Try running the web application to see the full system in action!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Optionally clean up (commented out to allow inspection)
        # shutil.rmtree(demo_dir)
        pass


if __name__ == "__main__":
    main()