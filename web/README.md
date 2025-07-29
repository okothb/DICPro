# DocProject Web Interface

A modern, responsive web interface for the DocProject Document Integrity Protection System.

## 🚀 Features

- **Modern UI**: Beautiful, responsive design with smooth animations
- **Drag & Drop**: Intuitive file upload with drag and drop support
- **Multiple Operations**: Protect, verify, extract, and batch processing
- **Real-time Feedback**: Progress indicators and status updates
- **Cross-platform**: Works on desktop and mobile devices

## 📁 Directory Structure

```
web/
├── index.html              # Main HTML file
├── static/
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   ├── js/
│   │   └── app.js         # JavaScript functionality
│   └── images/            # Image assets (if any)
└── README.md              # This file
```

## 🛠️ Setup and Usage

### Prerequisites

1. **FastAPI Backend**: Make sure the FastAPI server is running on `http://localhost:8000`
2. **Python 3.8+**: Required for the web server

### Starting the Web Server

1. **From the project root directory**, run:
   ```bash
   python web_server.py
   ```

2. **Or use Python's built-in server**:
   ```bash
   cd web
   python -m http.server 8080
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:8080
   ```

### Alternative: Using a Different Port

If port 8080 is in use, you can modify the port in `web_server.py`:

```python
PORT = 8081  # Change to any available port
```

## 🎯 Web Interface Features

### 1. Protect Documents
- Upload documents (PDF, DOCX, TXT, MD, PY, JS, HTML, CSS, PNG, JPG, BMP, TIFF)
- Enter secret data to embed
- Optional encryption with password
- Real-time processing feedback

### 2. Verify Documents
- Upload protected documents
- Verify integrity and authenticity
- View verification results with hash comparisons

### 3. Extract Data
- Extract embedded data from protected documents
- View extracted content and hash verification

### 4. Batch Processing
- Process multiple documents simultaneously
- Apply the same protection settings to all files
- View batch processing results

## 🔧 Configuration

### API Endpoint
The web interface connects to the FastAPI backend. To change the API URL, edit `static/js/app.js`:

```javascript
this.apiBaseUrl = 'http://localhost:8000'; // Change this URL
```

### CORS Settings
The web server includes CORS headers for development. For production, configure appropriate CORS settings in your FastAPI backend.

## 🎨 Customization

### Styling
- Modify `static/css/style.css` to customize the appearance
- The interface uses CSS custom properties for easy theming
- Responsive design works on all screen sizes

### Functionality
- Edit `static/js/app.js` to modify JavaScript behavior
- The app uses ES6 classes and modern JavaScript features
- API calls are handled with fetch() and FormData

## 🔍 Troubleshooting

### Common Issues

1. **"API not available" message**
   - Ensure the FastAPI server is running on port 8000
   - Check if the API endpoint is correct in `app.js`

2. **Files not uploading**
   - Check browser console for JavaScript errors
   - Ensure file types are supported
   - Verify file size limits

3. **Server won't start**
   - Check if port 8080 is already in use
   - Try a different port number
   - Ensure you're running from the project root directory

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript support required
- File API and FormData support needed

## 📱 Mobile Support

The web interface is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones
- Touch devices

## 🔒 Security Notes

- The web interface is for development and testing
- For production use, implement proper authentication
- Configure HTTPS for secure communication
- Set appropriate CORS policies

## 🚀 Development

### Adding New Features
1. Edit the HTML structure in `index.html`
2. Add corresponding CSS in `style.css`
3. Implement JavaScript functionality in `app.js`
4. Test with the FastAPI backend

### Building for Production
1. Minify CSS and JavaScript files
2. Optimize images and assets
3. Configure proper CORS and security headers
4. Use a production web server (nginx, Apache, etc.)

## 📞 Support

For issues or questions:
1. Check the browser console for errors
2. Verify the FastAPI backend is running
3. Review the API documentation at `http://localhost:8000/docs`
4. Check the main project README for backend setup

---

**Note**: This web interface is designed to work with the DocProject FastAPI backend. Make sure the backend is running before using the web interface. 