# DocProject User Manual

> **Installation:** See [User Installation Guide](user_installation_guide.md) for setup instructions.

This manual covers how to use the DocProject desktop application, including its features, workflow, and tips for best results.

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Getting Started](#getting-started)
5. [Main Features](#main-features)
6. [Step-by-Step Instructions](#step-by-step-instructions)
7. [Troubleshooting](#troubleshooting)
8. [Frequently Asked Questions](#frequently-asked-questions)
9. [Support](#support)

## Introduction

The Document Integrity Protection System is a security application designed to protect the authenticity and integrity of digital documents. This system uses advanced cryptographic techniques including SHA-256 hashing, AES encryption, and steganography to embed security information directly into documents.

### Key Benefits
- **Document Authentication**: Verify that documents haven't been tampered with
- **Invisible Protection**: Security information is hidden within the document itself
- **Multiple Formats**: Supports text documents, images, and various file types
- **User-Friendly**: Simple graphical interface for easy operation
- **Secure**: Uses industry-standard encryption algorithms

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 or later
- **Python Version**: Python 3.8 or higher
- **Memory**: 4 GB RAM minimum
- **Storage**: 100 MB free disk space
- **Display**: 1024x768 resolution minimum

### Recommended Requirements
- **Operating System**: Windows 11
- **Python Version**: Python 3.9+
- **Memory**: 8 GB RAM
- **Storage**: 500 MB free disk space
- **Display**: 1920x1080 resolution

### Required Software
- Python 3.8+ (download from python.org)
- PyCharm Community Edition (recommended IDE)
- Windows Defender exclusions may be needed

## Installation Guide

### Step 1: Install Python
1. Download Python 3.8+ from [python.org](https://python.org)
2. Run the installer and check "Add Python to PATH"
3. Verify installation by opening Command Prompt and typing: `python --version`

### Step 2: Download Project Files
1. Download the project folder: `document-integrity-project`
2. Extract to a convenient location (e.g., `C:\Projects\`)
3. Ensure all project files are present as shown in the project structure

### Step 3: Install Dependencies
1. Open Command Prompt as Administrator
2. Navigate to the project folder:
   ```
   cd C:\Projects\document-integrity-project
   ```
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Step 4: Verify Installation
1. Run the application:
   ```
   python main.py
   ```
2. The GUI should open without errors
3. If you see error messages, check the troubleshooting section

## Getting Started

### First Launch
1. Navigate to the project folder
2. Double-click `main.py` or run `python main.py` in Command Prompt
3. The main application window will open
4. You'll see the Document Integrity Protection System interface

### Main Interface Overview
The application consists of several key areas:
- **Menu Bar**: File operations and settings
- **Document Selection**: Choose files to protect or verify
- **Operation Buttons**: Protect, Verify, and other actions
- **Status Panel**: Shows current operation status
- **Results Display**: Shows verification results and messages

## Main Features

### 1. Document Protection
- **Hash Generation**: Creates SHA-256 hash of your document
- **Encryption**: Secures the hash using AES-256 encryption
- **Steganography**: Hides the encrypted hash within the document
- **Key Management**: Generates and manages encryption keys

### 2. Document Verification
- **Integrity Check**: Verifies if a document has been modified
- **Hash Extraction**: Retrieves hidden security information
- **Tampering Detection**: Identifies any unauthorized changes
- **Status Reporting**: Provides clear verification results

### 3. Supported File Types
- **Text Files**: .txt, .docx documents
- **PDF Files**: .pdf documents (read-only verification)
- **Image Files**: .png, .jpg, .bmp for steganography
- **Other Formats**: Additional formats may be supported

### 4. Security Features
- **AES-256 Encryption**: Military-grade encryption standard
- **SHA-256 Hashing**: Cryptographically secure hash function
- **Secure Key Storage**: Protected key management system
- **Invisible Embedding**: Steganographic techniques for hidden data

## Step-by-Step Instructions

### Protecting a Document

#### Step 1: Select Document
1. Click "Select Document" button
2. Browse and choose the file you want to protect
3. Supported formats: .txt, .docx, .png, .jpg
4. The selected file path will be displayed

#### Step 2: Choose Protection Method
1. **Text Steganography**: For text documents (.txt, .docx)
2. **Image Steganography**: For image files (.png, .jpg)
3. Select the appropriate method based on your file type

#### Step 3: Generate Protection
1. Click "Protect Document" button
2. The system will:
   - Generate SHA-256 hash of your document
   - Encrypt the hash using AES-256
   - Embed the encrypted hash using steganography
   - Save the protected document

#### Step 4: Save Protected Document
1. Choose a location to save the protected file
2. The original document remains unchanged
3. The protected document contains hidden security information
4. Keep the encryption key safe for future verification

### Verifying a Document

#### Step 1: Select Protected Document
1. Click "Select Document" for verification
2. Choose a document that was previously protected
3. Ensure you have the correct encryption key

#### Step 2: Load Encryption Key
1. Click "Load Key" button
2. Select the corresponding encryption key file
3. The key must match the one used for protection

#### Step 3: Verify Integrity
1. Click "Verify Document" button
2. The system will:
   - Extract hidden security information
   - Decrypt the embedded hash
   - Generate a new hash of the current document
   - Compare the hashes for verification

#### Step 4: Review Results
1. **VERIFIED**: Document is authentic and unchanged
2. **TAMPERED**: Document has been modified
3. **ERROR**: Verification failed (wrong key, corrupted file, etc.)

### Batch Processing (Advanced)

#### Processing Multiple Files
1. Click "Batch Process" menu option
2. Select multiple files using Ctrl+Click
3. Choose protection or verification mode
4. The system will process all files sequentially
5. Results will be saved to a report file

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start
**Problem**: Error when running `python main.py`
**Solutions**:
1. Verify Python installation: `python --version`
2. Check if all dependencies are installed: `pip list`
3. Reinstall requirements: `pip install -r requirements.txt --force-reinstall`
4. Try running as administrator

#### Missing Dependencies Error
**Problem**: "ModuleNotFoundError" when starting application
**Solutions**:
1. Ensure you're in the correct project directory
2. Install missing packages individually:
   ```
   pip install cryptography
   pip install pycryptodome
   pip install Pillow
   pip install python-docx
   ```
3. Update pip: `python -m pip install --upgrade pip`

#### File Access Denied
**Problem**: Cannot read or write files
**Solutions**:
1. Run application as administrator
2. Check file permissions
3. Ensure files are not open in other applications
4. Move files to a different location (avoid system folders)

#### Verification Always Fails
**Problem**: All documents show as "TAMPERED"
**Solutions**:
1. Verify you're using the correct encryption key
2. Check if the document format is supported
3. Ensure the document was properly protected initially
4. Try with a fresh document and key pair

#### GUI Display Issues
**Problem**: Interface appears corrupted or elements are missing
**Solutions**:
1. Update display drivers
2. Try different screen resolution
3. Check Windows scaling settings
4. Restart the application

### Error Messages and Meanings

| Error Message | Meaning | Solution |
|---------------|---------|----------|
| "Key file not found" | Encryption key is missing | Load the correct key file |
| "Unsupported file format" | File type not supported | Use .txt, .docx, .png, or .jpg files |
| "Hash mismatch detected" | Document has been modified | Document integrity compromised |
| "Decryption failed" | Wrong key or corrupted data | Verify correct key and file |
| "Access denied" | Insufficient permissions | Run as administrator |

## Frequently Asked Questions

### General Questions

**Q: What types of documents can I protect?**
A: The system supports text files (.txt, .docx), PDF files (verification only), and image files (.png, .jpg, .bmp).

**Q: How secure is the protection?**
A: The system uses AES-256 encryption and SHA-256 hashing, which are industry-standard security algorithms used by governments and financial institutions.

**Q: Can I protect multiple documents at once?**
A: Yes, use the batch processing feature to protect or verify multiple documents simultaneously.

**Q: What happens if I lose my encryption key?**
A: Without the encryption key, you cannot verify protected documents. Always keep backup copies of your keys in a secure location.

### Technical Questions

**Q: Does protection change my original document?**
A: No, the system creates a new protected version. Your original document remains unchanged.

**Q: Can someone detect that a document is protected?**
A: The steganographic techniques used make the protection virtually invisible to casual inspection.

**Q: How large can protected documents be?**
A: There's no strict size limit, but very large files (>100MB) may take longer to process.

**Q: Can I use this for commercial purposes?**
A: This is an academic project. For commercial use, consult with appropriate legal and security experts.

### Usage Questions

**Q: How do I share protected documents?**
A: You can share the protected document normally, but the recipient needs the encryption key to verify its integrity.

**Q: Can I protect already-protected documents?**
A: It's not recommended to apply protection multiple times. This may cause verification issues.

**Q: What if verification shows "TAMPERED" for an unchanged document?**
A: This usually indicates a wrong encryption key or file corruption. Try with the original key file.

## Support

### Getting Help

#### Documentation Resources
- **Technical Report**: Detailed implementation information
- **Code Comments**: Inline documentation in source files
- **README.md**: Quick setup and overview guide
- **This User Manual**: Comprehensive usage instructions

#### Self-Help Steps
1. Check the troubleshooting section above
2. Review error messages carefully
3. Verify system requirements are met
4. Try with sample documents first
5. Restart the application

#### Academic Support
For academic projects and assignments:
- Consult with your instructor or teaching assistant
- Review project requirements and grading criteria
- Use sample documents provided with the project
- Test all features before final submission

#### Technical Support
For technical issues:
1. Document the exact error message
2. Note the steps that led to the problem
3. Check if the issue occurs with sample files
4. Verify all dependencies are properly installed

### Additional Resources

#### Learning Materials
- **Cryptography Basics**: Understanding hashing and encryption
- **Steganography Concepts**: How data hiding works
- **Python Security Libraries**: Documentation for cryptography packages
- **GUI Development**: Tkinter tutorials and guides

#### Related Tools
- **File Comparison Tools**: To verify changes in documents
- **Hex Editors**: To examine file structures (advanced users)
- **Security Testing Tools**: For comprehensive security analysis

---

**Document Version**: 1.0  
**Last Updated**: June 2025  
**Author**: Document Integrity Protection System Team  
**Contact**: See project documentation for support information

This user manual provides comprehensive guidance for using the Document Integrity Protection System. For technical implementation details, refer to the Technical Report documentation.