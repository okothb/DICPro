# Netlify Deployment Setup Guide

## Quick Setup

1. **Deploy to Netlify:**
   - Connect your GitHub repository to Netlify
   - Set build directory to `web`
   - No build command needed (static files)

2. **Environment Variables (Optional - for full functionality):**
   ```
   UPSTASH_REDIS_REST_URL=your_redis_url_here
   UPSTASH_REDIS_REST_TOKEN=your_redis_token_here
   ```

3. **Test the deployment:**
   - Visit your Netlify URL
   - Click "Test API Connection" button
   - Should see ✅ API Connection Successful

## File Structure
```
web/                    # Static files (served by Netlify)
├── index.html         # Landing page
├── app.html          # Main application
└── static/
    ├── js/app.js     # Frontend JavaScript
    └── css/style.css # Styles

netlify/
└── functions/
    └── api.py        # Serverless function
```

## Features Available Without Redis
- ✅ API connection test
- ✅ Health check
- ✅ File upload interface
- ✅ Tab switching
- ❌ Document protection (requires Redis)
- ❌ Document verification (requires Redis)
- ❌ Data extraction (works without Redis)
- ❌ Batch processing (requires Redis)

## To Enable Full Functionality
1. Sign up for Upstash Redis (free tier available)
2. Get your REST URL and token
3. Add them as environment variables in Netlify
4. Redeploy

## Testing Locally
```bash
# Test the API function
python test_api_simple.py

# Start local web server
python -m http.server 8080 --directory web
```

Then visit http://localhost:8080/app.html