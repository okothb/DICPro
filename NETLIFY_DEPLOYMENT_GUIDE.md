# Netlify Deployment Guide for DocProject

This guide explains how to deploy the DocProject application to Netlify as a serverless application.

## Overview

The application has been converted from a continuously running Python server to serverless functions that work on Netlify. The conversion includes:

- **Frontend**: Static files served directly by Netlify
- **Backend**: Python serverless functions handling API requests
- **Core Logic**: Document processing modules copied to the functions directory

## Project Structure

```
├── web/                          # Frontend files (served by Netlify)
│   ├── index.html               # Main web interface
│   └── static/
│       ├── css/
│       └── js/
│           └── app.js           # Updated to work with serverless API
├── netlify/
│   └── functions/
│       ├── api.py               # Main serverless function
│       ├── requirements.txt     # Python dependencies
│       └── core/                # Core processing modules
│           ├── steganography.py
│           ├── hash_generator.py
│           ├── security.py
│           ├── security_validator.py
│           ├── path_validator.py
│           └── encryptor.py
├── netlify.toml                 # Netlify configuration
└── requirements.txt             # Original requirements (for reference)
```

## Deployment Steps

### 1. Prepare Your Repository

Ensure all files are committed to your Git repository:

```bash
git add .
git commit -m "Convert to Netlify serverless functions"
git push origin main
```

### 2. Connect to Netlify

1. Sign up for a [Netlify account](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect your GitHub account and select your repository
4. Configure the build settings:
   - **Build command**: Leave empty (no build needed)
   - **Publish directory**: `web`
   - **Functions directory**: `netlify/functions`

### 3. Configure Environment Variables (Optional)

If you need environment variables (like API keys), add them in Netlify:
1. Go to Site settings → Environment variables
2. Add any required variables

### 4. Deploy

Click "Deploy site" and Netlify will:
1. Pull your code from GitHub
2. Install Python dependencies from `netlify/functions/requirements.txt`
3. Deploy your static files from the `web` directory
4. Set up serverless functions from `netlify/functions`

## API Endpoints

The serverless function handles these endpoints:

- `GET /health` - Health check
- `POST /protect` - Protect documents with steganography
- `POST /verify` - Verify document integrity
- `POST /extract` - Extract embedded data
- `POST /batch-protect` - Batch document protection
- `POST /batch-verify` - Batch document verification
- `POST /validate-path` - Validate file paths

## Configuration Files

### netlify.toml

This file configures Netlify deployment:
- Sets `web` as the publish directory
- Sets `netlify/functions` as the functions directory
- Configures URL redirects to route API calls to serverless functions

### requirements.txt

Located in `netlify/functions/requirements.txt`, this specifies Python dependencies:
- Document processing libraries (Pillow, PyPDF2, openpyxl)
- Security libraries (cryptography, python-magic)
- Core dependencies (numpy, pandas)

## Frontend Changes

The JavaScript frontend (`web/static/js/app.js`) has been updated to:
- Use relative URLs for API calls in production
- Fall back to localhost:8000 for local development
- Work seamlessly with Netlify's serverless functions

## Limitations and Considerations

### File Processing Limitations

1. **Temporary Storage**: Serverless functions have limited temporary storage
2. **Execution Time**: Functions have timeout limits (typically 10 seconds for free tier)
3. **Memory**: Limited memory available for processing large files
4. **File Size**: Consider implementing file size limits for uploads

### Recommended Optimizations

1. **File Size Limits**: Implement client-side file size validation
2. **Async Processing**: For large files, consider using background processing
3. **Caching**: Implement caching for frequently accessed data
4. **Error Handling**: Robust error handling for network issues

## Local Development

To test locally before deployment:

1. **Frontend**: Serve the web directory with any static server
2. **Backend**: Run the original FastAPI server for development
3. **Testing**: Use the provided test script to verify function behavior

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all core modules are in `netlify/functions/core/`
2. **Dependency Issues**: Check `requirements.txt` for missing packages
3. **Path Issues**: Verify file paths are relative to the function directory
4. **CORS Issues**: Check CORS headers in the serverless function

### Debugging

1. Check Netlify function logs in the dashboard
2. Use the Netlify CLI for local testing
3. Verify file uploads work with small test files first

## Security Considerations

The application includes several security measures:
- Input validation for secret data
- File type validation
- Path traversal protection
- File size limits
- Content scanning

Ensure these are properly configured for your deployment environment.

## Next Steps

After successful deployment:
1. Test all functionality with various file types
2. Monitor function performance and errors
3. Consider implementing user authentication if needed
4. Set up monitoring and logging
5. Configure custom domain if desired

## Support

If you encounter issues:
1. Check Netlify function logs
2. Verify all dependencies are installed
3. Test with small files first
4. Check the original FastAPI implementation for reference