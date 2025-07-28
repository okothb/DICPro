# Document Integrity Protection System - Technical Report

## Executive Summary

The Document Integrity Protection System is a comprehensive security application designed to verify and protect the authenticity of digital documents through advanced cryptographic techniques. This system implements SHA-256 hashing, AES-256 encryption, and steganographic data hiding to create an invisible layer of protection that can detect document tampering while maintaining the original document's usability.

The project successfully demonstrates the practical application of cryptographic principles in document security, providing a user-friendly interface for non-technical users while maintaining robust security standards. The system achieves its primary objectives of document authentication, tamper detection, and secure data embedding across multiple file formats.

## 1. Introduction

### 1.1 Project Background
In today's digital landscape, document integrity and authenticity have become critical concerns for organizations and individuals. Traditional methods of document protection often rely on external security measures or visible modifications that can be easily circumvented or detected. This project addresses these limitations by implementing an integrated approach that embeds security information directly within documents using steganographic techniques.

### 1.2 Problem Statement
The primary challenges addressed by this system include:
- Detecting unauthorized modifications to digital documents
- Providing invisible security that doesn't alter document appearance
- Supporting multiple file formats commonly used in academic and professional environments
- Creating a user-friendly interface for security operations
- Implementing cryptographically secure protection mechanisms

### 1.3 Objectives
**Primary Objectives:**
- Develop a document integrity verification system using SHA-256 hashing
- Implement AES-256 encryption for security data protection
- Create steganographic techniques for invisible data embedding
- Design an intuitive graphical user interface using Tkinter
- Support multiple document formats (text, images, PDF)

**Secondary Objectives:**
- Implement batch processing capabilities
- Create comprehensive testing suite
- Develop detailed documentation and user guides
- Demonstrate practical application of cryptographic concepts
- Provide educational value for cybersecurity learning

### 1.4 Scope and Limitations
**Scope:**
- Document types: .txt, .docx, .pdf, .png, .jpg, .bmp
- Encryption: AES-256 with secure key management
- Hashing: SHA-256 for integrity verification
- Platform: Windows 10/11 with Python 3.8+
- Interface: Desktop application with GUI

**Limitations:**
- No network functionality or cloud storage
- Limited to single-user operation
- Requires encryption key for verification
- Performance depends on document size
- Academic project scope (not commercial-grade)

## 2. Literature Review and Theoretical Background

### 2.1 Cryptographic Hash Functions
Hash functions are fundamental to document integrity verification. SHA-256, chosen for this project, provides several critical properties:

**Deterministic**: The same input always produces the same hash output
**Avalanche Effect**: Small changes in input create dramatically different outputs
**Irreversible**: Computationally infeasible to derive input from hash
**Collision Resistant**: Extremely unlikely for different inputs to produce the same hash

The SHA-256 algorithm processes data in 512-bit chunks and produces a 256-bit digest, providing 2^256 possible hash values, ensuring virtually collision-free operation for practical applications.

### 2.2 Advanced Encryption Standard (AES)
AES-256 was selected for encrypting hash values due to its proven security and efficiency:

**Key Length**: 256-bit keys provide 2^256 possible combinations
**Block Size**: 128-bit blocks with 14 encryption rounds
**Security**: No known practical attacks against properly implemented AES-256
**Performance**: Optimized implementations available in hardware and software
**Standards Compliance**: NIST-approved and widely adopted globally

The encryption process uses the Cipher Block Chaining (CBC) mode with random initialization vectors to ensure semantic security.

### 2.3 Steganography Principles
Steganography, the practice of hiding information within other information, enables invisible data embedding:

**Text Steganography**: Utilizes whitespace manipulation, character encoding variations, and formatting adjustments to embed data without visual changes
**Image Steganography**: Employs Least Significant Bit (LSB) modification in pixel values, exploiting human visual system limitations
**Capacity vs. Invisibility Trade-off**: Balance between data payload and detection resistance

### 2.4 Related Work Analysis
Previous research in document security has explored various approaches:
- Digital signatures provide authentication but are visible and require infrastructure
- Watermarking techniques offer tamper detection but often affect document quality
- Blockchain-based solutions provide immutable records but require network connectivity
- Traditional encryption protects content but doesn't detect tampering after decryption

This project combines the advantages of multiple approaches while addressing their individual limitations.

## 3. System Architecture and Design

### 3.1 Overall System Architecture
The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    GUI Layer (Tkinter)                  │
├─────────────────────────────────────────────────────────┤
│                   Application Logic                     │
├─────────────────────────────────────────────────────────┤
│  Core Modules                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Hash         │ │ Encryption   │ │ Steganography│    │
│  │ Generator    │ │ Module       │ │ Module       │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│                   Utility Layer                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ File Handler │ │ Logger       │ │ Helpers      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│                 Operating System Layer                  │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Core Module Design

#### 3.2.1 Hash Generator Module
**Purpose**: Generate SHA-256 hashes of document content
**Key Functions**:
- `generate_hash(file_path)`: Creates hash from file content
- `generate_text_hash(text)`: Creates hash from text string
- `verify_hash(content, expected_hash)`: Compares computed vs. stored hash

**Implementation Details**:
```python
def generate_hash(self, file_path):
    """Generate SHA-256 hash of file content"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
```

#### 3.2.2 Encryption Module
**Purpose**: Secure hash values using AES-256 encryption
**Key Functions**:
- `generate_key()`: Creates random 256-bit encryption key
- `encrypt_data(data, key)`: Encrypts data using AES-256-CBC
- `decrypt_data(encrypted_data, key)`: Decrypts previously encrypted data
- `key_from_password(password)`: Derives key from user password

**Security Features**:
- Random initialization vectors for each encryption
- PBKDF2 key derivation for password-based keys
- Proper padding for block cipher requirements
- Secure random number generation

#### 3.2.3 Steganography Module
**Purpose**: Hide encrypted data within documents
**Key Functions**:
- `embed_text_data(text, data)`: Hide data in text using whitespace
- `extract_text_data(text)`: Retrieve hidden data from text
- `embed_image_data(image, data)`: Hide data using LSB in images
- `extract_image_data(image)`: Retrieve data from image LSBs

**Text Steganography Algorithm**:
1. Convert data to binary representation
2. Insert extra spaces at sentence boundaries
3. Use tab characters vs. spaces to represent binary 0/1
4. Maintain natural text appearance and formatting

**Image Steganography Algorithm**:
1. Convert data to binary representation
2. Modify least significant bits of pixel values
3. Distribute data across RGB channels
4. Preserve image visual quality

### 3.3 GUI Architecture
The graphical user interface is built using Tkinter with a component-based approach:

**Main Window Components**:
- Menu bar with File, Edit, and Help menus
- Document selection frame with file browser
- Operation selection frame with radio buttons
- Progress display with status bar and progress bar
- Results display with scrollable text area

**Event-Driven Architecture**:
- Button clicks trigger corresponding core module functions
- File dialogs handle document selection
- Progress callbacks update GUI during long operations
- Error handling displays user-friendly messages

### 3.4 Data Flow Architecture
The system processes documents through the following data flow:

**Protection Process**:
1. User selects document file
2. System generates SHA-256 hash of content
3. Hash is encrypted using AES-256
4. Encrypted hash is embedded using steganography
5. Protected document is saved to output directory

**Verification Process**:
1. User selects protected document
2. System extracts embedded data using steganography
3. Embedded data is decrypted using provided key
4. New hash is generated from current document content
5. Hashes are compared to determine integrity status

## 4. Implementation Details

### 4.1 Development Environment
**Programming Language**: Python 3.9.7
**IDE**: PyCharm Community Edition 2023.1
**Operating System**: Windows 11 Professional
**Version Control**: Git with local repository
**Dependencies Management**: pip with requirements.txt

### 4.2 Key Dependencies and Libraries

#### 4.2.1 Cryptography Libraries
```python
# cryptography==41.0.7 - Modern cryptographic library
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# pycryptodome==3.19.0 - Additional cryptographic functions
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
```

#### 4.2.2 File Processing Libraries
```python
# Pillow==10.1.0 - Image processing for steganography
from PIL import Image, ImageTk
import numpy as np

# python-docx==1.1.0 - Microsoft Word document processing
import docx
from docx import Document

# PyPDF2==3.0.1 - PDF file processing
import PyPDF2
```

#### 4.2.3 GUI and Utility Libraries
```python
# tkinter - Standard GUI library (included with Python)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Standard library utilities
import hashlib, os, json, logging, base64
```

### 4.3 Core Algorithm Implementations

#### 4.3.1 Document Hashing Implementation
```python
class HashGenerator:
    def __init__(self):
        self.algorithm = 'sha256'
    
    def generate_file_hash(self, file_path):
        """Generate SHA-256 hash of entire file content"""
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as file:
                # Process file in chunks to handle large files
                for chunk in iter(lambda: file.read(8192), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        
        except IOError as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    def generate_text_hash(self, text_content):
        """Generate hash from text string"""
        if isinstance(text_content, str):
            text_content = text_content.encode('utf-8')
        
        return hashlib.sha256(text_content).hexdigest()
```

#### 4.3.2 AES Encryption Implementation
```python
class AESEncryptor:
    def __init__(self):
        self.key_size = 32  # 256 bits
        self.block_size = 16  # 128 bits
    
    def generate_key(self):
        """Generate random 256-bit key"""
        return get_random_bytes(self.key_size)
    
    def encrypt_data(self, data, key):
        """Encrypt data using AES-256-CBC"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate random IV
        iv = get_random_bytes(self.block_size)
        
        # Create cipher object
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad data to block size
        padded_data = pad(data, self.block_size)
        
        # Encrypt data
        encrypted_data = cipher.encrypt(padded_data)
        
        # Return IV + encrypted data
        return base64.b64encode(iv + encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data, key):
        """Decrypt AES-256-CBC encrypted data"""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract IV and encrypted data
            iv = encrypted_bytes[:self.block_size]
            encrypted_content = encrypted_bytes[self.block_size:]
            
            # Create cipher object
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # Decrypt and unpad
            decrypted_data = unpad(cipher.decrypt(encrypted_content), self.block_size)
            
            return decrypted_data.decode('utf-8')
        
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
```

#### 4.3.3 Text Steganography Implementation
```python
class TextSteganography:
    def __init__(self):
        self.delimiter = '\u200B'  # Zero-width space
        self.encoding_marker = '\u200C'  # Zero-width non-joiner
    
    def embed_data_in_text(self, text, data):
        """Hide data in text using zero-width characters"""
        # Convert data to binary
        binary_data = ''.join(format(ord(char), '08b') for char in data)
        
        # Add marker and length information
        data_length = format(len(binary_data), '032b')
        full_binary = self.encoding_marker + data_length + binary_data
        
        # Embed binary data using zero-width characters
        sentences = text.split('.')
        embedded_text = ""
        binary_index = 0
        
        for sentence in sentences:
            if sentence.strip():
                embedded_text += sentence
                
                # Embed bits using zero-width characters
                if binary_index < len(full_binary):
                    if full_binary[binary_index] == '1':
                        embedded_text += self.delimiter
                    binary_index += 1
                
                embedded_text += '.'
        
        return embedded_text
    
    def extract_data_from_text(self, text):
        """Extract hidden data from text"""
        try:
            # Look for encoding marker
            if self.encoding_marker not in text:
                return None
            
            # Extract binary data using zero-width characters
            binary_bits = ""
            for char in text:
                if char == self.delimiter:
                    binary_bits += '1'
                elif char in [' ', '\t', '\n']:
                    binary_bits += '0'
            
            # Extract length information
            if len(binary_bits) < 32:
                return None
            
            data_length = int(binary_bits[:32], 2)
            data_binary = binary_bits[32:32+data_length]
            
            # Convert binary back to text
            data = ""
            for i in range(0, len(data_binary), 8):
                byte = data_binary[i:i+8]
                if len(byte) == 8:
                    data += chr(int(byte, 2))
            
            return data
        
        except Exception:
            return None
```

#### 4.3.4 Image Steganography Implementation
```python
class ImageSteganography:
    def __init__(self):
        self.max_bits_per_channel = 2  # Use 2 LSBs for better capacity
    
    def embed_data_in_image(self, image_path, data):
        """Hide data in image using LSB steganography"""
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Convert data to binary
        binary_data = ''.join(format(ord(char), '08b') for char in data)
        
        # Add delimiter and length information
        data_length = format(len(binary_data), '032b')
        full_binary = '1111111111111110' + data_length + binary_data + '1111111111111111'
        
        # Check if image can hold the data
        total_pixels = img_array.shape[0] * img_array.shape[1]
        available_bits = total_pixels * 3 * self.max_bits_per_channel  # RGB channels
        
        if len(full_binary) > available_bits:
            raise Exception("Image too small to hold the data")
        
        # Embed data in LSBs
        binary_index = 0
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(3):  # RGB channels
                    if binary_index < len(full_binary):
                        # Modify LSB
                        pixel_value = img_array[i, j, k]
                        bit_value = int(full_binary[binary_index])
                        
                        # Clear LSB and set new value
                        pixel_value = (pixel_value & 0xFE) | bit_value
                        img_array[i, j, k] = pixel_value
                        
                        binary_index += 1
        
        # Save modified image
        result_img = Image.fromarray(img_array)
        return result_img
    
    def extract_data_from_image(self, image_path):
        """Extract hidden data from image"""
        try:
            # Load image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Extract binary data from LSBs
            binary_data = ""
            for i in range(img_array.shape[0]):
                for j in range(img_array.shape[1]):
                    for k in range(3):  # RGB channels
                        pixel_value = img_array[i, j, k]
                        binary_data += str(pixel_value & 1)  # Get LSB
            
            # Look for start delimiter
            start_marker = '1111111111111110'
            start_index = binary_data.find(start_marker)
            
            if start_index == -1:
                return None
            
            # Extract length
            length_start = start_index + len(start_marker)
            length_binary = binary_data[length_start:length_start + 32]
            data_length = int(length_binary, 2)
            
            # Extract actual data
            data_start = length_start + 32
            data_binary = binary_data[data_start:data_start + data_length]
            
            # Convert binary to text
            data = ""
            for i in range(0, len(data_binary), 8):
                byte = data_binary[i:i+8]
                if len(byte) == 8:
                    data += chr(int(byte, 2))
            
            return data
        
        except Exception:
            return None
```

### 4.4 GUI Implementation Details

#### 4.4.

## Output Folder Selection

The application now requires users to select a destination folder for all protected (output) files. This ensures that no output files are stored within the application directory, giving users full control over file storage locations.

## Responsive User Interface

The user interface has been updated to automatically fit the device screen or browser window, improving usability across different platforms and devices.

## Commercial License

A commercial license has been added to the project to protect intellectual property, restrict unauthorized distribution, and give the owner full control over resale, pricing, redistribution, and branding.

## REST API Architecture

The application now includes a comprehensive REST API built with FastAPI that provides programmatic access to all document protection and verification features. The API follows RESTful principles and includes comprehensive documentation.

### API Components

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Pydantic Models**: Data validation and serialization
- **CORS Middleware**: Cross-origin resource sharing support
- **File Upload Handling**: Secure multipart file uploads
- **Temporary File Management**: Automatic cleanup of processed files
- **Health Monitoring**: API status and component health checks

### API Endpoints

#### Core Endpoints
- `GET /`: API root information and version
- `GET /health`: Health check and component status
- `POST /protect`: Single document protection
- `POST /verify`: Document integrity verification
- `POST /extract`: Data extraction from protected documents
- `POST /batch-protect`: Batch document processing
- `GET /download/{file_id}`: Protected file download
- `DELETE /cleanup`: Temporary file cleanup

#### Request/Response Models
- **ProtectionRequest**: Document protection parameters
- **ProtectionResponse**: Protection operation results
- **VerificationResponse**: Verification status and data
- **ExtractionResponse**: Extracted data and hash information
- **BatchResponse**: Batch processing summary
- **HealthResponse**: API health status

### API Features

#### Document Protection
- Support for all file types (PDF, images, Excel)
- Optional payload encryption
- Hash generation and storage
- Processing time tracking

#### Document Verification
- Integrity checking via hash comparison
- Data extraction capabilities
- Verification status reporting

#### Batch Processing
- Multiple file upload support
- Individual file result tracking
- Success/failure statistics

#### File Management
- Temporary file storage with automatic cleanup
- Secure file download endpoints
- File type validation

### Integration Capabilities

#### Web Applications
- CORS support for browser-based clients
- FormData upload support
- JSON response format

#### Mobile Applications
- RESTful API design
- Standard HTTP methods
- Error handling and status codes

#### Enterprise Systems
- Batch processing capabilities
- Health monitoring endpoints
- Configurable server settings

### Security Considerations

#### File Upload Security
- File type validation
- Temporary file isolation
- Automatic cleanup mechanisms

#### API Security
- Input validation via Pydantic
- Error handling without information disclosure
- CORS configuration for production

#### Data Protection
- Secure file handling
- Hash-based integrity verification
- Optional payload encryption

### Performance Optimization

#### File Processing
- Asynchronous request handling
- Temporary file management
- Memory-efficient file operations

#### API Response
- Structured JSON responses
- Minimal data transfer
- Efficient error reporting

### Deployment Configuration

#### Environment Variables
- `DOCPROJECT_HOST`: Server host address
- `DOCPROJECT_PORT`: Server port number
- `DOCPROJECT_RELOAD`: Development reload mode
- `DOCPROJECT_LOG_LEVEL`: Logging verbosity

#### Production Considerations
- Reverse proxy configuration
- SSL/TLS termination
- Rate limiting implementation
- Authentication and authorization