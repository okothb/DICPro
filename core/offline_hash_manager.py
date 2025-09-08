"""
Offline-First Hash Storage Manager
Provides local storage with cloud sync capabilities for document hashes.
"""

import os
import json
import sqlite3
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import threading
import time
import requests
from dataclasses import dataclass, asdict
import uuid


@dataclass
class HashRecord:
    """Data class for hash records"""
    id: str
    original_filename: str
    original_hash: str
    protected_hash: str
    secret_data_hash: str
    created_at: str
    synced_at: Optional[str] = None
    sync_status: str = "pending"  # pending, synced, failed
    file_size: int = 0
    protection_method: str = "unknown"


class OfflineHashManager:
    """
    Manages document hashes with offline-first approach.
    Stores locally and syncs to backend when online.
    """
    
    def __init__(self, local_db_path: str = None, backend_url: str = None):
        """Initialize the offline hash manager"""
        self.local_db_path = local_db_path or os.path.join("data", "local_hashes.db")
        self.backend_url = backend_url or "http://localhost:8000"
        self.output_hash_dir = os.path.join("output", "hash")
        self.sync_lock = threading.Lock()
        self.auto_sync_enabled = True
        self.sync_interval = 300  # 5 minutes
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)
        os.makedirs(self.output_hash_dir, exist_ok=True)
        
        # Initialize local database
        self._init_local_db()
        
        # Start background sync if enabled
        if self.auto_sync_enabled:
            self._start_background_sync()
    
    def _init_local_db(self):
        """Initialize local SQLite database for hash storage"""
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS hash_records (
                        id TEXT PRIMARY KEY,
                        original_filename TEXT NOT NULL,
                        original_hash TEXT NOT NULL,
                        protected_hash TEXT NOT NULL,
                        secret_data_hash TEXT,
                        created_at TEXT NOT NULL,
                        synced_at TEXT,
                        sync_status TEXT DEFAULT 'pending',
                        file_size INTEGER DEFAULT 0,
                        protection_method TEXT DEFAULT 'unknown',
                        metadata TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_original_filename 
                    ON hash_records(original_filename)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_protected_hash 
                    ON hash_records(protected_hash)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sync_status 
                    ON hash_records(sync_status)
                """)
                
                conn.commit()
                print(f"✅ Local hash database initialized: {self.local_db_path}")
        except Exception as e:
            print(f"❌ Failed to initialize local database: {e}")
            raise
    
    def store_hash_offline(self, original_filename: str, original_hash: str, 
                          protected_hash: str, secret_data: bytes = None,
                          protection_method: str = "unknown", 
                          file_size: int = 0) -> str:
        """
        Store hash record locally (offline-first)
        Returns the record ID
        """
        try:
            record_id = str(uuid.uuid4())
            secret_data_hash = None
            
            if secret_data:
                secret_data_hash = hashlib.sha256(secret_data).hexdigest()
            
            record = HashRecord(
                id=record_id,
                original_filename=original_filename,
                original_hash=original_hash,
                protected_hash=protected_hash,
                secret_data_hash=secret_data_hash,
                created_at=datetime.now().isoformat(),
                sync_status="pending",
                file_size=file_size,
                protection_method=protection_method
            )
            
            # Store in local database
            with sqlite3.connect(self.local_db_path) as conn:
                conn.execute("""
                    INSERT INTO hash_records 
                    (id, original_filename, original_hash, protected_hash, 
                     secret_data_hash, created_at, sync_status, file_size, protection_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.id, record.original_filename, record.original_hash,
                    record.protected_hash, record.secret_data_hash, record.created_at,
                    record.sync_status, record.file_size, record.protection_method
                ))
                conn.commit()
            
            # Also store in output/hash directory as JSON file
            self._store_hash_file(record)
            
            print(f"✅ Hash stored locally: {original_filename} -> {record_id}")
            
            # Trigger immediate sync attempt if online
            if self._is_online():
                threading.Thread(target=self._sync_single_record, args=(record_id,)).start()
            
            return record_id
            
        except Exception as e:
            print(f"❌ Failed to store hash offline: {e}")
            raise
    
    def _store_hash_file(self, record: HashRecord):
        """Store hash record as JSON file in output/hash directory"""
        try:
            filename = f"{record.original_filename}_{record.id}.hash.json"
            filepath = os.path.join(self.output_hash_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(asdict(record), f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to store hash file: {e}")
    
    def get_hash_by_filename(self, filename: str, hash_type: str = "protected") -> Optional[str]:
        """
        Retrieve hash by filename (offline-first)
        """
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                cursor = conn.execute("""
                    SELECT original_hash, protected_hash 
                    FROM hash_records 
                    WHERE original_filename = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (filename,))
                
                result = cursor.fetchone()
                if result:
                    original_hash, protected_hash = result
                    return protected_hash if hash_type == "protected" else original_hash
                
                # If not found locally, try to sync and search again
                if self._is_online():
                    self._sync_from_backend(filename)
                    cursor = conn.execute("""
                        SELECT original_hash, protected_hash 
                        FROM hash_records 
                        WHERE original_filename = ? 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """, (filename,))
                    
                    result = cursor.fetchone()
                    if result:
                        original_hash, protected_hash = result
                        return protected_hash if hash_type == "protected" else original_hash
                
                return None
                
        except Exception as e:
            print(f"❌ Failed to retrieve hash: {e}")
            return None
    
    def get_hash_record(self, filename: str) -> Optional[HashRecord]:
        """Get complete hash record by filename"""
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM hash_records 
                    WHERE original_filename = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (filename,))
                
                result = cursor.fetchone()
                if result:
                    return HashRecord(
                        id=result[0],
                        original_filename=result[1],
                        original_hash=result[2],
                        protected_hash=result[3],
                        secret_data_hash=result[4],
                        created_at=result[5],
                        synced_at=result[6],
                        sync_status=result[7],
                        file_size=result[8],
                        protection_method=result[9]
                    )
                return None
                
        except Exception as e:
            print(f"❌ Failed to get hash record: {e}")
            return None
    
    def verify_document_offline(self, filename: str, current_hash: str) -> Dict[str, Any]:
        """
        Verify document integrity using local hash storage
        """
        try:
            record = None
            with sqlite3.connect(self.local_db_path) as conn:
                # Search for the record using the hash of the file provided for verification.
                # This hash should match the 'protected_hash' if the file is a valid protected file.
                cursor = conn.execute("""
                    SELECT * FROM hash_records 
                    WHERE protected_hash = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (current_hash,))
                
                result = cursor.fetchone()
                if result:
                    record = HashRecord(
                        id=result[0],
                        original_filename=result[1],
                        original_hash=result[2],
                        protected_hash=result[3],
                        secret_data_hash=result[4],
                        created_at=result[5],
                        synced_at=result[6],
                        sync_status=result[7],
                        file_size=result[8],
                        protection_method=result[9]
                    )

            if not record:
                # If no record is found, the file is either tampered, or it's an original file,
                # or it's a file whose hash was never stored.
                # In all cases, we can't find a matching protected hash.
                # Returning "no_hash_found" is consistent with the original code's failure mode,
                # and it solves the primary bug where valid files were not being found.
                return {
                    'verified': False,
                    'status': 'no_hash_found',
                    'message': 'No stored hash found for this document',
                    'current_hash': current_hash,
                    'stored_hash': None
                }
            
            # If we found a record, it means current_hash matches a stored protected_hash.
            # The document is therefore verified.
            is_verified = True
            
            return {
                'verified': is_verified,
                'status': 'verified',
                'message': 'Document verified successfully',
                'current_hash': current_hash,
                'stored_hash': record.protected_hash,
                'original_hash': record.original_hash,
                'protection_date': record.created_at,
                'sync_status': record.sync_status
            }
            
        except Exception as e:
            return {
                'verified': False,
                'status': 'error',
                'message': f'Verification failed: {str(e)}',
                'current_hash': current_hash,
                'stored_hash': None
            }
    
    def _is_online(self) -> bool:
        """Check if backend is accessible"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _sync_single_record(self, record_id: str):
        """Sync a single record to backend"""
        try:
            with self.sync_lock:
                with sqlite3.connect(self.local_db_path) as conn:
                    cursor = conn.execute("""
                        SELECT * FROM hash_records WHERE id = ?
                    """, (record_id,))
                    
                    result = cursor.fetchone()
                    if not result:
                        return
                    
                    record = HashRecord(
                        id=result[0],
                        original_filename=result[1],
                        original_hash=result[2],
                        protected_hash=result[3],
                        secret_data_hash=result[4],
                        created_at=result[5],
                        synced_at=result[6],
                        sync_status=result[7],
                        file_size=result[8],
                        protection_method=result[9]
                    )
                    
                    # Send to backend
                    response = requests.post(f"{self.backend_url}/hash/store", 
                                           json=asdict(record), timeout=10)
                    
                    if response.status_code == 200:
                        # Update sync status
                        conn.execute("""
                            UPDATE hash_records 
                            SET sync_status = 'synced', synced_at = ? 
                            WHERE id = ?
                        """, (datetime.now().isoformat(), record_id))
                        conn.commit()
                        print(f"✅ Synced record: {record.original_filename}")
                    else:
                        # Mark as failed
                        conn.execute("""
                            UPDATE hash_records 
                            SET sync_status = 'failed' 
                            WHERE id = ?
                        """, (record_id,))
                        conn.commit()
                        print(f"❌ Failed to sync record: {record.original_filename}")
                        
        except Exception as e:
            print(f"❌ Sync failed for record {record_id}: {e}")
    
    def _sync_from_backend(self, filename: str):
        """Sync hash records from backend for a specific filename"""
        try:
            response = requests.get(f"{self.backend_url}/hash/get/{filename}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('records'):
                    for record_data in data['records']:
                        # Store in local database if not exists
                        with sqlite3.connect(self.local_db_path) as conn:
                            conn.execute("""
                                INSERT OR IGNORE INTO hash_records 
                                (id, original_filename, original_hash, protected_hash, 
                                 secret_data_hash, created_at, sync_status, file_size, protection_method, synced_at)
                                VALUES (?, ?, ?, ?, ?, ?, 'synced', ?, ?, ?)
                            """, (
                                record_data.get('id', str(uuid.uuid4())),
                                record_data['original_filename'],
                                record_data['original_hash'],
                                record_data['protected_hash'],
                                record_data.get('secret_data_hash'),
                                record_data['created_at'],
                                record_data.get('file_size', 0),
                                record_data.get('protection_method', 'unknown'),
                                datetime.now().isoformat()
                            ))
                            conn.commit()
                            
        except Exception as e:
            print(f"❌ Failed to sync from backend: {e}")
    
    def sync_all_pending(self) -> Dict[str, int]:
        """Sync all pending records to backend"""
        stats = {'synced': 0, 'failed': 0, 'skipped': 0}
        
        if not self._is_online():
            print("❌ Backend not accessible, skipping sync")
            return stats
        
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                cursor = conn.execute("""
                    SELECT id FROM hash_records WHERE sync_status = 'pending'
                """)
                
                pending_ids = [row[0] for row in cursor.fetchall()]
                
                for record_id in pending_ids:
                    try:
                        self._sync_single_record(record_id)
                        stats['synced'] += 1
                    except:
                        stats['failed'] += 1
                        
        except Exception as e:
            print(f"❌ Batch sync failed: {e}")
            
        return stats
    
    def _start_background_sync(self):
        """Start background sync thread"""
        def sync_worker():
            while self.auto_sync_enabled:
                try:
                    if self._is_online():
                        stats = self.sync_all_pending()
                        if stats['synced'] > 0:
                            print(f"🔄 Background sync: {stats['synced']} records synced")
                except Exception as e:
                    print(f"❌ Background sync error: {e}")
                
                time.sleep(self.sync_interval)
        
        sync_thread = threading.Thread(target=sync_worker, daemon=True)
        sync_thread.start()
        print("🔄 Background sync started")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                cursor = conn.execute("""
                    SELECT sync_status, COUNT(*) 
                    FROM hash_records 
                    GROUP BY sync_status
                """)
                
                status_counts = dict(cursor.fetchall())
                
                cursor = conn.execute("SELECT COUNT(*) FROM hash_records")
                total_records = cursor.fetchone()[0]
                
                return {
                    'total_records': total_records,
                    'pending': status_counts.get('pending', 0),
                    'synced': status_counts.get('synced', 0),
                    'failed': status_counts.get('failed', 0),
                    'online': self._is_online(),
                    'last_sync_attempt': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'online': False,
                'total_records': 0
            }
    
    def cleanup_old_records(self, days: int = 30):
        """Clean up old synced records"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.local_db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM hash_records 
                    WHERE sync_status = 'synced' AND synced_at < ?
                """, (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"🧹 Cleaned up {deleted_count} old records")
                return deleted_count
                
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return 0
    
    def export_hashes(self, output_file: str) -> bool:
        """Export all hash records to JSON file"""
        try:
            with sqlite3.connect(self.local_db_path) as conn:
                cursor = conn.execute("SELECT * FROM hash_records")
                records = []
                
                for row in cursor.fetchall():
                    record = HashRecord(
                        id=row[0],
                        original_filename=row[1],
                        original_hash=row[2],
                        protected_hash=row[3],
                        secret_data_hash=row[4],
                        created_at=row[5],
                        synced_at=row[6],
                        sync_status=row[7],
                        file_size=row[8],
                        protection_method=row[9]
                    )
                    records.append(asdict(record))
                
                with open(output_file, 'w') as f:
                    json.dump({
                        'exported_at': datetime.now().isoformat(),
                        'total_records': len(records),
                        'records': records
                    }, f, indent=2)
                
                print(f"📤 Exported {len(records)} records to {output_file}")
                return True
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False