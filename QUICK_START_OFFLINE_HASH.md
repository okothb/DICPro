# Quick Start: Offline-First Hash Storage

## 🚀 Getting Started

### 1. Start the Enhanced API Server

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the API server with offline-first hash management
python api.py
```

The server will automatically:
- ✅ Initialize the offline hash storage system
- ✅ Create the `output/hash` directory for backend storage
- ✅ Set up SQLite database for local hash storage
- ✅ Start background synchronization service

### 2. Access the Web Application

Open your browser and navigate to:
- **Local Development**: `http://localhost:8080` (if using simple web server)
- **API Direct**: `http://localhost:8000` (FastAPI server)

### 3. Explore the New Hash Management Tab

Click on the **"Hash Storage"** tab to access:

#### 📊 Storage Statistics
- View total hash records
- Monitor sync status (pending/synced/failed)
- Check storage usage and file sizes
- See online/offline status

#### 🔄 Synchronization Controls
- Manual sync trigger
- Real-time sync progress
- Background sync status
- Connection monitoring

#### 📋 Hash Record Management
- Browse recent hash records
- View all stored hashes
- Export hash data to JSON
- Search and filter records

#### 🧹 Maintenance Tools
- Clean up old synchronized records
- Optimize database storage
- Export/backup hash data
- System health monitoring

## 📱 Offline Usage

### Protecting Documents Offline

1. **Disconnect from internet** (or work in airplane mode)
2. **Upload documents** in the "Protect Documents" tab
3. **Add secret data** and configure protection settings
4. **Click "Protect Documents"** - works without internet!
5. **Hashes stored locally** - will sync when connection restored

### Verifying Documents Offline

1. **Upload protected documents** in the "Verify Documents" tab
2. **Click "Verify Documents"** - uses local hash storage
3. **Get instant results** - no internet required for verification
4. **See sync status** - shows if hash was synced to cloud

## 🔧 Testing the System

### Run the Demo

```bash
# Interactive demonstration of offline-first features
python demo_offline_hash_system.py
```

This will show you:
- Document protection workflow
- Offline verification capabilities
- Sync status management
- Hash storage statistics
- Export/import functionality

### Run the Test Suite

```bash
# Comprehensive testing of all features
python test_offline_hash_system.py
```

Tests include:
- Offline hash storage
- Document verification accuracy
- Synchronization logic
- API endpoint functionality
- Performance benchmarks

## 🌐 API Usage Examples

### Store Hash (Offline-First)

```bash
curl -X POST "http://localhost:8000/hash/store" \
  -H "Content-Type: application/json" \
  -d '{
    "original_filename": "document.pdf",
    "original_hash": "abc123...",
    "protected_hash": "def456...",
    "protection_method": "pdf_steganography",
    "file_size": 1024
  }'
```

### Verify Document

```bash
curl -X POST "http://localhost:8000/hash/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "document.pdf",
    "current_hash": "def456..."
  }'
```

### Get Sync Status

```bash
curl "http://localhost:8000/hash/sync/status"
```

### Trigger Manual Sync

```bash
curl -X POST "http://localhost:8000/hash/sync/all"
```

## 📁 File Locations

### Local Storage
- **Database**: `data/local_hashes.db`
- **Hash Files**: `output/hash/*.hash.json`
- **Exports**: `temp/hash_export_*.json`

### Configuration
- **API Base URL**: Configurable in `web/app.html`
- **Sync Interval**: 5 minutes (configurable)
- **Auto-sync**: Enabled by default

## 🔍 Monitoring & Troubleshooting

### Check System Status

1. **Hash Management Tab**: Real-time status dashboard
2. **Browser Console**: JavaScript logs and errors
3. **API Logs**: Server-side operation logs
4. **Database**: Direct SQLite inspection if needed

### Common Issues

#### "No stored hash found"
- Document hasn't been protected yet
- Filename mismatch between protection and verification
- Hash record not synced from another device

#### "Sync failed"
- Backend server not accessible
- Network connectivity issues
- Authentication problems (if configured)

#### "Database locked"
- Multiple processes accessing same database
- Background sync in progress
- File permission issues

### Solutions

1. **Check online status** in Hash Management tab
2. **Trigger manual sync** when connection restored
3. **Export hash data** for backup before troubleshooting
4. **Restart application** if database issues persist

## 🎯 Best Practices

### For Document Protection
1. **Always use unique filenames** for better hash matching
2. **Keep original files safe** - hashes verify integrity, not content
3. **Regular sync** when online to ensure cloud backup
4. **Export hash data** periodically for additional backup

### For System Management
1. **Monitor sync status** regularly
2. **Clean up old records** to optimize storage
3. **Export important hashes** before major changes
4. **Test offline functionality** before critical usage

### For Development
1. **Use test environment** for development and testing
2. **Check API endpoints** with proper error handling
3. **Monitor performance** with large hash datasets
4. **Implement proper logging** for production deployment

## 🚀 Advanced Usage

### Custom Configuration

```python
# Initialize with custom settings
from core.offline_hash_manager import OfflineHashManager

hash_manager = OfflineHashManager(
    local_db_path="custom/path/hashes.db",
    backend_url="https://your-api.com",
    sync_interval=600,  # 10 minutes
    auto_sync_enabled=True
)
```

### Batch Operations

```python
# Bulk hash storage
for document in documents:
    hash_manager.store_hash_offline(
        original_filename=document.name,
        original_hash=document.original_hash,
        protected_hash=document.protected_hash,
        protection_method="batch_processing"
    )

# Bulk verification
results = []
for document in documents:
    result = hash_manager.verify_document_offline(
        document.name, 
        document.current_hash
    )
    results.append(result)
```

### Integration with Existing Systems

```python
# Add to existing FastAPI app
from api_hash_endpoints import integrate_hash_endpoints

app = FastAPI()
integrate_hash_endpoints(app)  # Adds all hash management routes
```

## 📞 Support

For issues or questions:

1. **Check the logs** in browser console and server output
2. **Run the test suite** to verify system functionality
3. **Try the demo** to understand expected behavior
4. **Review the documentation** in `OFFLINE_FIRST_HASH_STORAGE_IMPLEMENTATION.md`

---

**You're now ready to use the offline-first hash storage system!** 🎉

The system provides enterprise-grade document protection with the convenience of offline operation and automatic cloud synchronization.