# Netlify Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. **Environment Variables** ⚠️ CRITICAL
- [ ] `UPSTASH_REDIS_REST_URL` - Set in Netlify dashboard
- [ ] `UPSTASH_REDIS_REST_TOKEN` - Set in Netlify dashboard
- [ ] Test Redis connection from Upstash console

### 2. **File Structure** ✅ READY
- [x] `netlify.toml` - Build and redirect configuration
- [x] `netlify/functions/api.py` - Main serverless function
- [x] `netlify/functions/hash_manager_netlify.py` - Hash management for serverless
- [x] `netlify_requirements.txt` - Python dependencies
- [x] `web/` directory - Static files (HTML, CSS, JS)

### 3. **Dependencies** ✅ READY
- [x] All core modules compatible with serverless
- [x] Redis-based hash storage (no local SQLite)
- [x] Lightweight dependencies in `netlify_requirements.txt`
- [x] Cross-platform magic library for file type detection

### 4. **API Endpoints** ✅ READY
- [x] `/protect` - Document protection
- [x] `/verify` - Document verification  
- [x] `/extract` - Data extraction
- [x] `/batch-protect` - Batch protection
- [x] `/batch-verify` - Batch verification
- [x] `/hash/store` - Hash storage
- [x] `/hash/get/{filename}` - Hash retrieval
- [x] `/hash/verify` - Hash verification
- [x] `/hash/sync/status` - Sync status
- [x] `/hash/list` - List hashes
- [x] `/hash/stats` - Hash statistics
- [x] `/hash/export` - Export hashes
- [x] `/health` - Health check
- [x] `/test` - Simple test endpoint

### 5. **Frontend Integration** ✅ READY
- [x] Hash Management tab in web interface
- [x] Offline/online status indicators
- [x] API base URL configured for Netlify Functions
- [x] Error handling for serverless environment

## 🚀 Deployment Steps

### 1. **Connect Repository**
1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Click "New site from Git"
3. Connect your GitHub/GitLab repository
4. Select the repository with your code

### 2. **Configure Build Settings**
- **Build command**: (leave empty - Netlify handles Python dependencies automatically)
- **Publish directory**: `web`
- **Functions directory**: `netlify/functions`

### 3. **Set Environment Variables**
1. Go to Site settings → Environment variables
2. Add `UPSTASH_REDIS_REST_URL`
3. Add `UPSTASH_REDIS_REST_TOKEN`
4. Save and trigger a new deploy

### 4. **Test Deployment**
1. Wait for build to complete
2. Test health endpoint: `https://your-site.netlify.app/.netlify/functions/api/health`
3. Test hash management: `https://your-site.netlify.app/.netlify/functions/api/hash/sync/status`
4. Test web interface: `https://your-site.netlify.app/app`

## 🔧 Post-Deployment Verification

### API Tests
```bash
# Health check
curl https://your-site.netlify.app/.netlify/functions/api/health

# Hash sync status
curl https://your-site.netlify.app/.netlify/functions/api/hash/sync/status

# Test endpoint
curl https://your-site.netlify.app/.netlify/functions/api/test
```

### Web Interface Tests
1. Open `https://your-site.netlify.app/app`
2. Test document protection (upload a small file)
3. Check Hash Storage tab functionality
4. Verify offline/online status indicators

## ⚠️ Common Issues & Solutions

### **Issue: "Redis not available"**
**Solution**: 
- Check environment variables are set correctly
- Verify Redis instance is active in Upstash
- Check function logs in Netlify dashboard

### **Issue: "Module not found"**
**Solution**:
- Ensure `netlify_requirements.txt` is complete
- Check Python version compatibility
- Verify build command in `netlify.toml`

### **Issue: "Function timeout"**
**Solution**:
- Optimize file processing for large files
- Consider implementing file size limits
- Use streaming for large operations

### **Issue: "CORS errors"**
**Solution**:
- Verify CORS headers in API responses
- Check API base URL in frontend
- Test with browser developer tools

## 📊 Performance Considerations

### **Serverless Limitations**
- **Execution time**: 10 seconds max per function call
- **Memory**: 1008 MB max
- **File size**: 6 MB max for uploads
- **Cold starts**: First request may be slower

### **Optimizations Applied**
- ✅ Redis for fast hash storage/retrieval
- ✅ Minimal dependencies to reduce cold start time
- ✅ Efficient file processing algorithms
- ✅ Error handling to prevent timeouts
- ✅ Streaming responses for large data

## 🎯 Success Criteria

Your deployment is successful when:

- [ ] Health endpoint returns 200 OK
- [ ] Hash sync status shows Redis connected
- [ ] Document protection works end-to-end
- [ ] Hash Management tab loads and functions
- [ ] No console errors in browser
- [ ] All API endpoints respond correctly

## 📞 Support

If you encounter issues:

1. **Check Netlify Function Logs**:
   - Go to Netlify dashboard → Functions → View logs
   - Look for error messages and stack traces

2. **Test Locally**:
   ```bash
   netlify dev
   ```

3. **Verify Environment**:
   - Check all environment variables are set
   - Test Redis connection from Upstash console

4. **Review Documentation**:
   - `NETLIFY_ENVIRONMENT_SETUP.md`
   - `OFFLINE_FIRST_HASH_STORAGE_IMPLEMENTATION.md`

---

**Your offline-first hash storage system is now ready for Netlify deployment!** 🚀