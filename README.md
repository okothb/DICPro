# Document Integrity Protection System

**Undergraduate Project - Computer Security & Cryptography**

A Python-based application that ensures document integrity through cryptographic hashing, AES encryption, and steganographic techniques. This system allows users to protect their documents and verify their authenticity.

## 🚀 Features

### Core Features
- **Document Hashing**: Generate SHA-256 hashes of documents
- **AES Encryption**: Encrypt hash values with AES-256
- **Multi-format Steganography**: Hide encrypted hashes in various document types
- **Document Verification**: Extract and verify document integrity
- **GUI Interface**: User-friendly Tkinter-based interface
- **Multi-format Support**: Handle .txt, .docx, .pdf, and image files

### Steganography Methods
- **Image Steganography**: LSB (Least Significant Bit) method for PNG, JPG, BMP, TIFF
- **Text Steganography**: Whitespace encoding for .txt, .md, .py, .js, .html, .css
- **DOCX Steganography**: Metadata embedding for Microsoft Word documents
- **PDF Steganography**: Metadata embedding for PDF documents with integrity verification

### Bonus Features
- **Advanced PDF Support**: Robust PDF steganography with metadata validation
- **Drag and Drop Interface**: Intuitive file handling with visual drop zones
- **Batch Processing**: Process multiple files simultaneously
- **Key Management**: Generate and securely store encryption keys
- **Comprehensive Logging**: Track all operations and errors
- **File Type Detection**: Automatic detection and appropriate steganography method selection

## 📁 Project Structure

```
document-integrity-project/
│
├── 📄 main.py                          # Main application entry point
├── 📄 requirements.txt                 # Python dependencies
├── 📄 config.py                        # Configuration settings
├── 📄 README.md                        # Project documentation
├── 📄 .gitignore                       # Git ignore file
│
├── 📁 core/                            # Core functionality modules
│   ├── 📄 __init__.py
│   ├── 📄 hash_generator.py            # Document hashing (SHA-256)
│   ├── 📄 encryptor.py                 # AES encryption/decryption
│   ├── 📄 steganography.py             # Hide/extract data in documents
│   └── 📄 verifier.py                  # Document integrity verification
│
├── 📁 gui/                             # Tkinter GUI application
│   ├── 📄 __init__.py
│   ├── 📄 main_window.py               # Main application window
│   ├── 📄 components.py                # Reusable GUI components
│   └── 📄 styles.py                    # GUI styling and themes
│
├── 📁 utils/                           # Utility functions
│   ├── 📄 __init__.py
│   ├── 📄 file_handler.py              # File operations
│   ├── 📄 logger.py                    # Simple logging
│   └── 📄 helpers.py                   # Helper functions
│
├── 📁 data/                            # Data storage
│   ├── 📁 input/                       # Input documents
│   ├── 📁 output/                      # Processed documents
│   ├── 📁 keys/                        # Encryption keys
│   └── 📁 logs/                        # Application logs
│
├── 📁 tests/                           # Unit tests
│   ├── 📄 __init__.py
│   ├── 📄 test_hash_generator.py
│   ├── 📄 test_encryptor.py
│   ├── 📄 test_steganography.py
│   └── 📄 test_verifier.py
│
├── 📁 samples/                         # Sample documents for testing
│   ├── 📄 sample_certificate.txt
│   ├── 📄 sample_transcript.txt
│   └── 📄 sample_image.png
│
└── 📁 docs/                            # Project documentation
    ├── 📄 user_manual.md               # How to use the application
    ├── 📄 technical_report.md          # Technical implementation details
    └── 📁 screenshots/                 # GUI screenshots for report
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary development environment)
- PyCharm Community Edition (recommended IDE)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd document-integrity-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create necessary directories**
   ```bash
   mkdir data\input data\output data\keys data\logs
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## 📦 Dependencies

The project uses the following main libraries:

- **cryptography==41.0.7** - Core cryptographic operations
- **pycryptodome==3.19.0** - AES encryption/decryption
- **Pillow==10.1.0** - Image processing for steganography
- **python-docx==1.1.0** - Microsoft Word document handling
- **PyPDF2==3.0.1** - PDF document processing
- **numpy==1.24.3** - Numerical operations

See `requirements.txt` for the complete list.

## 🎯 Usage

### Basic Workflow

1. **Protect a Document**:
   - Launch the application
   - **Option A**: Drag and drop your file onto the Protect tab or drop zone
   - **Option B**: Select "Protect Document" option and browse for files
   - The system automatically detects file type and applies appropriate steganography
   - Save the protected document

2. **Verify Document Integrity**:
   - **Option A**: Drag and drop your file onto the Verify tab or drop zone
   - **Option B**: Select "Verify Document" option and browse for files
   - The system extracts steganographic data and verifies document integrity
   - View detailed verification results including steganographic metadata

3. **Analyze Files**:
   - Drag and drop any file onto the Results tab or drop zone
   - Get instant analysis including file type, size, hash, and steganographic data detection

### Supported File Types

| File Type | Steganography Method | Description |
|-----------|---------------------|-------------|
| **Images** (.png, .jpg, .bmp, .tiff) | LSB (Least Significant Bit) | Hides data in pixel values |
| **Text Files** (.txt, .md, .py, etc.) | Whitespace Encoding | Hides data using spaces and tabs |
| **DOCX Files** (.docx) | Metadata Embedding | Hides data in document properties |
| **PDF Files** (.pdf) | Metadata Embedding | Hides data in PDF metadata with integrity checks |

### Drag and Drop Usage

The application features intuitive drag and drop functionality:

```bash
# Install drag and drop support
pip install tkinterdnd2

# Run the application
python main.py

# Then simply drag files from your file explorer to:
# - Protect tab: For document protection
# - Verify tab: For document verification  
# - Results tab: For file analysis
```

### Command Line Usage

For advanced users, core functions can be accessed via command line:

```bash
# Generate hash of a document
python -m core.hash_generator document.txt

# Encrypt a hash
python -m core.encryptor hash_value key_file

# Verify document integrity
python -m core.verifier protected_document.txt
```

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_hash_generator.py

# Run with coverage report
python -m pytest tests/ --cov=core --cov-report=html

# Test PDF steganography specifically
python test_pdf_steganography.py

# Test drag and drop functionality
python test_drag_and_drop.py
```

### Test Categories

- **Unit Tests**: Test individual modules and functions
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Edge Case Tests**: Handle unusual inputs and scenarios

## 📊 Development Phases

### Phase 1: Core Functionality (Weeks 1-2)
- [x] Document hashing with SHA-256
- [x] AES encryption/decryption
- [x] Basic file I/O operations
- [x] Console-based testing

### Phase 2: Steganography (Weeks 3-4)
- [x] Text steganography implementation
- [x] Image steganography (LSB method)
- [x] Data extraction functions
- [x] Integration testing

### Phase 3: GUI Development (Weeks 5-6)
- [x] Main window design
- [x] File upload/download interface
- [x] Progress indicators
- [x] Results display

### Phase 4: Testing & Documentation (Weeks 7-8)
- [x] Unit tests for all modules
- [x] User manual creation
- [x] Technical report writing
- [x] Demo preparation

## 🏗️ Architecture

### Core Components

- **Hash Generator**: Creates SHA-256 hashes of input documents
- **Encryptor**: Handles AES-256 encryption and decryption
- **Steganography Module**: Implements text and image steganography
- **Verifier**: Extracts and validates embedded integrity data
- **GUI Layer**: Provides user-friendly interface
- **Utilities**: File handling, logging, and helper functions

### Security Considerations

- Uses industry-standard SHA-256 hashing
- Implements AES-256 encryption for hash protection
- Secure key generation and management
- Protection against common tampering attempts
- Comprehensive error handling and logging

## 📋 Configuration

Edit `config.py` to customize application settings:

```python
# Application settings
APP_NAME = "Document Integrity Protection System"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Security settings
KEY_SIZE = 32  # AES-256
HASH_ALGORITHM = "sha256"

# File paths
INPUT_DIR = "data/input"
OUTPUT_DIR = "data/output"
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Errors**: Run as administrator if needed on Windows

3. **File Path Issues**: Use absolute paths or ensure working directory is correct

4. **Tkinter Not Found**: Install tkinter (usually comes with Python)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   ```

## 📚 Documentation

- **User Manual**: `docs/user_manual.md` - Step-by-step usage guide
- **Technical Report**: `docs/technical_report.md` - Implementation details
- **API Documentation**: Generated from docstrings
- **Screenshots**: `docs/screenshots/` - GUI examples

## 🤝 Contributing

This is an academic project, but suggestions and improvements are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is created for educational purposes as part of an undergraduate computer security course.

## 👨‍💻 Author

**[Your Name]** - Student ID: [Your Student ID]  
Computer Science Department  
[Your University Name]

## 🙏 Acknowledgments

- Course instructor and teaching assistants
- Python cryptography community
- Open source libraries and their maintainers
- Academic resources and research papers referenced

## 📞 Support

For questions or issues:
- Email: [your.email@university.edu]
- Course Forum: [Link to course discussion board]
- Office Hours: [Schedule and location]

---

**Note**: This project is developed for academic purposes to demonstrate understanding of cryptographic principles and secure software development practices.

## Recent Updates

- The application now prompts users to select a destination folder for all protected (output) files. Output files are no longer stored in the application's own directories; users have full control over where protected files are saved.
- The user interface is now fully responsive and automatically fits the device screen or browser window, providing a better experience on all devices and window sizes.
- A commercial license has been added to protect the intellectual property of the application. Redistribution, resale, and branding are restricted as per the license terms.

## Packaging the Flet Desktop App

You can package this Flet app as a standalone desktop application for Windows, Mac, or Linux.

### 1. Install Requirements

Make sure you have Python 3.8+ and pip installed. Then install dependencies:

```bash
pip install -r requirements.txt
pip install flet pyinstaller
```

### 2. Test the App Locally

Run the app to ensure everything works:

```bash
python app.py
```

### 3. Package with PyInstaller

Use the provided packaging script or run the following command:

```bash
pyinstaller --noconfirm --onefile --windowed --icon=DocPro.ico app.py
```

- `--onefile`: Bundle into a single executable
- `--windowed`: No console window (for GUI apps)
- `--icon=DocPro.ico`: Use your app icon (optional)

The output executable will be in the `dist/` folder.

### 4. Packaging Script

You can use the following script to automate packaging (save as `package_app.sh` for Mac/Linux or `package_app.bat` for Windows):

#### Windows (`package_app.bat`):
```bat
@echo off
pip install -r requirements.txt
pip install flet pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon=DocPro.ico app.py
```

#### Mac/Linux (`package_app.sh`):
```sh
#!/bin/bash
pip install -r requirements.txt
pip install flet pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon=DocPro.ico app.py
```

### 5. Run the Packaged App

- On Windows: `dist\app.exe`
- On Mac/Linux: `./dist/app`

### 6. Notes
- You may need to adjust the icon path or app name as needed.
- For advanced options, see the [PyInstaller documentation](https://pyinstaller.org/en/stable/).
- Flet also supports [native packaging](https://flet.dev/docs/desktop/packaging/) for more advanced use cases.

---

## API Integration

DocProject now includes a comprehensive REST API that provides programmatic access to all document protection and verification features. The API is built with FastAPI and supports both single document processing and batch operations.

### API Features

- **Document Protection**: Embed secret data in documents using steganography
- **Document Verification**: Verify document integrity and extract embedded data
- **Batch Processing**: Process multiple documents simultaneously
- **File Upload/Download**: Secure file handling with temporary storage
- **Health Monitoring**: API health checks and status monitoring
- **CORS Support**: Cross-origin resource sharing for web applications
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc

### Quick Start

1. **Start the API Server**:
   ```bash
   python start_api.py
   # or
   python api.py
   ```

2. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

3. **Use the API Client**:
   ```bash
   python api_client_example.py
   ```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root information |
| GET | `/health` | Health check and status |
| POST | `/protect` | Protect a single document |
| POST | `/verify` | Verify document integrity |
| POST | `/extract` | Extract embedded data |
| POST | `/batch-protect` | Protect multiple documents |
| GET | `/download/{file_id}` | Download protected file |
| DELETE | `/cleanup` | Clean up temporary files |

### Example Usage

#### Protect a Document
```python
import requests

# Upload and protect a document
with open('document.pdf', 'rb') as f:
    files = {'file': ('document.pdf', f, 'application/pdf')}
    data = {
        'secret_data': 'Secret message to embed',
        'encrypt_payload': False
    }
    response = requests.post('http://localhost:8000/protect', files=files, data=data)
    result = response.json()
    print(f"Protected file: {result['protected_file']}")
```

#### Verify Document Integrity
```python
# Verify a protected document
with open('protected_document.pdf', 'rb') as f:
    files = {'file': ('protected_document.pdf', f, 'application/pdf')}
    response = requests.post('http://localhost:8000/verify', files=files)
    result = response.json()
    print(f"Verified: {result['is_verified']}")
```

#### Batch Processing
```python
# Process multiple files
files = []
for file_path in ['doc1.pdf', 'doc2.png', 'doc3.xlsx']:
    with open(file_path, 'rb') as f:
        files.append(('files', (file_path, f, 'application/octet-stream')))

data = {'secret_data': 'Batch secret message'}
response = requests.post('http://localhost:8000/batch-protect', files=files, data=data)
result = response.json()
print(f"Processed {result['successful']} out of {result['total_files']} files")
```

### API Client Library

A complete Python client library is provided in `api_client_example.py` that demonstrates:

- Document protection with encryption
- Document verification and integrity checking
- Data extraction from protected documents
- Batch processing capabilities
- File download functionality
- Error handling and validation

### Configuration

The API server can be configured using environment variables:

```bash
export DOCPROJECT_HOST="0.0.0.0"
export DOCPROJECT_PORT="8000"
export DOCPROJECT_RELOAD="false"
export DOCPROJECT_LOG_LEVEL="info"
```

### Security Considerations

- **CORS Configuration**: Configure `allow_origins` in production
- **File Upload Limits**: Implement file size and type restrictions
- **Authentication**: Add API key or JWT authentication for production
- **Rate Limiting**: Implement request rate limiting
- **Temporary Files**: Files are automatically cleaned up after 1 hour

### Integration Examples

#### Web Application Integration
```javascript
// JavaScript example for web applications
async function protectDocument(file, secretData) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('secret_data', secretData);
    
    const response = await fetch('http://localhost:8000/protect', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

#### Mobile App Integration
```python
# Python requests for mobile apps
import requests

def protect_document_api(file_path, secret_data, api_url):
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'secret_data': secret_data}
        response = requests.post(f"{api_url}/protect", files=files, data=data)
        return response.json()
```