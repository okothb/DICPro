"""
Enhanced API Endpoints for Offline-First Hash Management
Provides REST API for hash storage, retrieval, and synchronization.
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.offline_hash_manager import OfflineHashManager, HashRecord


# Pydantic models for API requests/responses
class HashStoreRequest(BaseModel):
    original_filename: str = Field(..., description="Original filename")
    original_hash: str = Field(..., description="Hash of original document")
    protected_hash: str = Field(..., description="Hash of protected document")
    secret_data_hash: Optional[str] = Field(None, description="Hash of secret data")
    protection_method: str = Field("unknown", description="Protection method used")
    file_size: int = Field(0, description="File size in bytes")


class HashVerifyRequest(BaseModel):
    filename: str = Field(..., description="Filename to verify")
    current_hash: str = Field(..., description="Current hash of the document")


class HashResponse(BaseModel):
    success: bool
    message: str
    record_id: Optional[str] = None
    hash_value: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None


class VerificationResponse(BaseModel):
    success: bool
    verified: bool
    status: str
    message: str
    current_hash: str
    stored_hash: Optional[str]
    original_hash: Optional[str] = None
    protection_date: Optional[str] = None
    sync_status: Optional[str] = None


class SyncStatusResponse(BaseModel):
    success: bool
    total_records: int
    pending: int
    synced: int
    failed: int
    online: bool
    last_sync_attempt: str


def create_hash_api_routes(app: FastAPI):
    """Add hash management routes to FastAPI app"""
    
    # Initialize hash manager
    hash_manager = OfflineHashManager()
    
    @app.post("/hash/store", response_model=HashResponse)
    async def store_hash(request: HashStoreRequest, background_tasks: BackgroundTasks):
        """
        Store a hash record (offline-first)
        """
        try:
            record_id = hash_manager.store_hash_offline(
                original_filename=request.original_filename,
                original_hash=request.original_hash,
                protected_hash=request.protected_hash,
                secret_data=request.secret_data_hash.encode() if request.secret_data_hash else None,
                protection_method=request.protection_method,
                file_size=request.file_size
            )
            
            return HashResponse(
                success=True,
                message="Hash stored successfully",
                record_id=record_id
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store hash: {str(e)}")
    
    @app.get("/hash/get/{filename}", response_model=HashResponse)
    async def get_hash(filename: str, hash_type: str = "protected"):
        """
        Retrieve hash by filename
        """
        try:
            hash_value = hash_manager.get_hash_by_filename(filename, hash_type)
            
            if hash_value:
                record = hash_manager.get_hash_record(filename)
                return HashResponse(
                    success=True,
                    message="Hash retrieved successfully",
                    hash_value=hash_value,
                    records=[{
                        'id': record.id,
                        'original_filename': record.original_filename,
                        'original_hash': record.original_hash,
                        'protected_hash': record.protected_hash,
                        'created_at': record.created_at,
                        'sync_status': record.sync_status,
                        'protection_method': record.protection_method
                    }] if record else None
                )
            else:
                return HashResponse(
                    success=False,
                    message="Hash not found",
                    hash_value=None
                )
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve hash: {str(e)}")
    
    @app.post("/hash/verify", response_model=VerificationResponse)
    async def verify_hash(request: HashVerifyRequest):
        """
        Verify document integrity using stored hash
        """
        try:
            result = hash_manager.verify_document_offline(
                filename=request.filename,
                current_hash=request.current_hash
            )
            
            return VerificationResponse(
                success=True,
                verified=result['verified'],
                status=result['status'],
                message=result['message'],
                current_hash=result['current_hash'],
                stored_hash=result['stored_hash'],
                original_hash=result.get('original_hash'),
                protection_date=result.get('protection_date'),
                sync_status=result.get('sync_status')
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")
    
    @app.get("/hash/sync/status", response_model=SyncStatusResponse)
    async def get_sync_status():
        """
        Get synchronization status
        """
        try:
            status = hash_manager.get_sync_status()
            
            return SyncStatusResponse(
                success=True,
                total_records=status.get('total_records', 0),
                pending=status.get('pending', 0),
                synced=status.get('synced', 0),
                failed=status.get('failed', 0),
                online=status.get('online', False),
                last_sync_attempt=status.get('last_sync_attempt', datetime.now().isoformat())
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")
    
    @app.post("/hash/sync/all")
    async def sync_all_hashes(background_tasks: BackgroundTasks):
        """
        Trigger synchronization of all pending hashes
        """
        try:
            def sync_task():
                stats = hash_manager.sync_all_pending()
                print(f"Sync completed: {stats}")
            
            background_tasks.add_task(sync_task)
            
            return JSONResponse(
                status_code=202,
                content={
                    "success": True,
                    "message": "Synchronization started in background"
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start sync: {str(e)}")
    
    @app.get("/hash/list")
    async def list_hashes(limit: int = 50, offset: int = 0, sync_status: Optional[str] = None):
        """
        List hash records with pagination
        """
        try:
            import sqlite3
            
            query = "SELECT * FROM hash_records"
            params = []
            
            if sync_status:
                query += " WHERE sync_status = ?"
                params.append(sync_status)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            with sqlite3.connect(hash_manager.local_db_path) as conn:
                cursor = conn.execute(query, params)
                records = []
                
                for row in cursor.fetchall():
                    records.append({
                        'id': row[0],
                        'original_filename': row[1],
                        'original_hash': row[2],
                        'protected_hash': row[3],
                        'secret_data_hash': row[4],
                        'created_at': row[5],
                        'synced_at': row[6],
                        'sync_status': row[7],
                        'file_size': row[8],
                        'protection_method': row[9]
                    })
                
                # Get total count
                count_query = "SELECT COUNT(*) FROM hash_records"
                count_params = []
                if sync_status:
                    count_query += " WHERE sync_status = ?"
                    count_params.append(sync_status)
                
                cursor = conn.execute(count_query, count_params)
                total_count = cursor.fetchone()[0]
                
                return {
                    "success": True,
                    "records": records,
                    "total": total_count,
                    "limit": limit,
                    "offset": offset
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list hashes: {str(e)}")
    
    @app.delete("/hash/cleanup")
    async def cleanup_old_hashes(days: int = 30):
        """
        Clean up old synced hash records
        """
        try:
            deleted_count = hash_manager.cleanup_old_records(days)
            
            return {
                "success": True,
                "message": f"Cleaned up {deleted_count} old records",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
    
    @app.get("/hash/export")
    async def export_hashes():
        """
        Export all hash records to JSON
        """
        try:
            export_file = f"hash_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = os.path.join("temp", export_file)
            
            # Ensure temp directory exists
            os.makedirs("temp", exist_ok=True)
            
            success = hash_manager.export_hashes(export_path)
            
            if success:
                return {
                    "success": True,
                    "message": "Hash records exported successfully",
                    "export_file": export_file,
                    "download_url": f"/download/{export_file}"
                }
            else:
                raise HTTPException(status_code=500, detail="Export failed")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    
    @app.get("/hash/stats")
    async def get_hash_stats():
        """
        Get hash storage statistics
        """
        try:
            import sqlite3
            
            with sqlite3.connect(hash_manager.local_db_path) as conn:
                # Get basic stats
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN sync_status = 'pending' THEN 1 END) as pending,
                        COUNT(CASE WHEN sync_status = 'synced' THEN 1 END) as synced,
                        COUNT(CASE WHEN sync_status = 'failed' THEN 1 END) as failed,
                        AVG(file_size) as avg_file_size,
                        SUM(file_size) as total_file_size
                    FROM hash_records
                """)
                
                stats = cursor.fetchone()
                
                # Get protection method distribution
                cursor = conn.execute("""
                    SELECT protection_method, COUNT(*) 
                    FROM hash_records 
                    GROUP BY protection_method
                """)
                
                methods = dict(cursor.fetchall())
                
                # Get recent activity (last 7 days)
                cursor = conn.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM hash_records 
                    WHERE created_at >= datetime('now', '-7 days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """)
                
                recent_activity = dict(cursor.fetchall())
                
                return {
                    "success": True,
                    "stats": {
                        "total_records": stats[0] or 0,
                        "pending_sync": stats[1] or 0,
                        "synced": stats[2] or 0,
                        "failed_sync": stats[3] or 0,
                        "avg_file_size": round(stats[4] or 0, 2),
                        "total_file_size": stats[5] or 0
                    },
                    "protection_methods": methods,
                    "recent_activity": recent_activity,
                    "online": hash_manager._is_online()
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# Integration function for existing API
def integrate_hash_endpoints(app: FastAPI):
    """
    Integrate hash management endpoints into existing FastAPI app
    """
    create_hash_api_routes(app)
    print("✅ Hash management endpoints integrated")