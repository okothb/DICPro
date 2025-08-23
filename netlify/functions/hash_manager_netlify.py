"""
Netlify-Compatible Hash Manager
Uses Upstash Redis instead of local SQLite for serverless deployment
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
import hashlib

try:
    from upstash_redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    Redis = None
    REDIS_AVAILABLE = False


class NetlifyHashManager:
    """
    Hash manager optimized for Netlify serverless functions
    Uses Upstash Redis for storage instead of local SQLite
    """
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = None
        self.redis_loaded = False
        
        if REDIS_AVAILABLE:
            try:
                redis_url = os.environ.get("UPSTASH_REDIS_REST_URL")
                redis_token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
                
                if redis_url and redis_token:
                    self.redis_client = Redis(url=redis_url, token=redis_token)
                    self.redis_client.ping()  # Test connection
                    self.redis_loaded = True
                    print("✅ Netlify hash manager connected to Redis")
                else:
                    print("⚠️ Redis credentials not found in environment")
            except Exception as e:
                print(f"❌ Failed to connect to Redis: {e}")
                self.redis_loaded = False
    
    def store_hash_record(self, original_filename: str, original_hash: str, 
                         protected_hash: str, secret_data_hash: str = None,
                         protection_method: str = "unknown", file_size: int = 0) -> str:
        """
        Store hash record in Redis
        Returns record ID
        """
        if not self.redis_loaded:
            raise Exception("Redis not available for hash storage")
        
        record_id = str(uuid.uuid4())
        
        record_data = {
            "id": record_id,
            "original_filename": original_filename,
            "original_hash": original_hash,
            "protected_hash": protected_hash,
            "secret_data_hash": secret_data_hash,
            "protection_method": protection_method,
            "file_size": file_size,
            "created_at": datetime.now().isoformat(),
            "sync_status": "synced"  # Already in cloud
        }
        
        # Store with protected_hash as key for fast lookup
        self.redis_client.set(f"hash:{protected_hash}", json.dumps(record_data))
        
        # Also store with filename for lookup by name
        self.redis_client.set(f"file:{original_filename}", json.dumps(record_data))
        
        # Add to index for listing
        self.redis_client.sadd("hash_index", record_id)
        
        return record_id
    
    def get_hash_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve hash record by filename
        """
        if not self.redis_loaded:
            return None
        
        try:
            record_json = self.redis_client.get(f"file:{filename}")
            if record_json:
                return json.loads(record_json)
            return None
        except Exception as e:
            print(f"Error retrieving hash for {filename}: {e}")
            return None
    
    def get_hash_by_protected_hash(self, protected_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve hash record by protected hash
        """
        if not self.redis_loaded:
            return None
        
        try:
            record_json = self.redis_client.get(f"hash:{protected_hash}")
            if record_json:
                return json.loads(record_json)
            return None
        except Exception as e:
            print(f"Error retrieving hash record: {e}")
            return None
    
    def verify_document(self, filename: str, current_hash: str) -> Dict[str, Any]:
        """
        Verify document integrity using stored hash
        """
        try:
            # First try to find by protected hash (direct match)
            record = self.get_hash_by_protected_hash(current_hash)
            
            if record:
                return {
                    'verified': True,
                    'status': 'verified',
                    'message': 'Document verified successfully',
                    'current_hash': current_hash,
                    'stored_hash': record['protected_hash'],
                    'original_hash': record['original_hash'],
                    'protection_date': record['created_at'],
                    'sync_status': 'synced'
                }
            
            # If not found by hash, try by filename
            record = self.get_hash_by_filename(filename)
            
            if record:
                is_verified = current_hash == record['protected_hash']
                return {
                    'verified': is_verified,
                    'status': 'verified' if is_verified else 'tampered',
                    'message': 'Document verified successfully' if is_verified else 'Document may have been tampered with',
                    'current_hash': current_hash,
                    'stored_hash': record['protected_hash'],
                    'original_hash': record['original_hash'],
                    'protection_date': record['created_at'],
                    'sync_status': 'synced'
                }
            
            return {
                'verified': False,
                'status': 'no_hash_found',
                'message': 'No stored hash found for this document',
                'current_hash': current_hash,
                'stored_hash': None
            }
            
        except Exception as e:
            return {
                'verified': False,
                'status': 'error',
                'message': f'Verification failed: {str(e)}',
                'current_hash': current_hash,
                'stored_hash': None
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get hash storage statistics
        """
        if not self.redis_loaded:
            return {
                'total_records': 0,
                'online': False,
                'error': 'Redis not available'
            }
        
        try:
            # Get total count from index
            total_records = self.redis_client.scard("hash_index")
            
            return {
                'total_records': total_records,
                'pending_sync': 0,  # All records are already synced in cloud
                'synced': total_records,
                'failed_sync': 0,
                'online': True,
                'last_sync_attempt': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'total_records': 0,
                'online': False,
                'error': str(e)
            }
    
    def list_hashes(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        List hash records with pagination
        """
        if not self.redis_loaded:
            return {
                'success': False,
                'records': [],
                'total': 0,
                'error': 'Redis not available'
            }
        
        try:
            # Get all record IDs from index
            all_ids = list(self.redis_client.smembers("hash_index"))
            total = len(all_ids)
            
            # Apply pagination
            paginated_ids = all_ids[offset:offset + limit]
            
            records = []
            for record_id in paginated_ids:
                # Find the record by scanning hash keys
                # This is not optimal but works for small datasets
                for key in self.redis_client.scan_iter(match="hash:*"):
                    record_json = self.redis_client.get(key)
                    if record_json:
                        record = json.loads(record_json)
                        if record.get('id') == record_id:
                            records.append(record)
                            break
            
            return {
                'success': True,
                'records': records,
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            return {
                'success': False,
                'records': [],
                'total': 0,
                'error': str(e)
            }
    
    def export_hashes(self) -> Dict[str, Any]:
        """
        Export all hash records
        """
        if not self.redis_loaded:
            return {
                'success': False,
                'error': 'Redis not available'
            }
        
        try:
            all_records = []
            
            # Scan all hash records
            for key in self.redis_client.scan_iter(match="hash:*"):
                record_json = self.redis_client.get(key)
                if record_json:
                    record = json.loads(record_json)
                    all_records.append(record)
            
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'total_records': len(all_records),
                'records': all_records,
                'source': 'netlify_redis'
            }
            
            return {
                'success': True,
                'data': export_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Cleanup old records (placeholder for Netlify)
        In serverless environment, we typically don't need cleanup
        """
        # In Netlify/serverless, we usually don't implement cleanup
        # as storage is managed and costs are minimal
        return 0
    
    def is_available(self) -> bool:
        """Check if hash manager is available"""
        return self.redis_loaded