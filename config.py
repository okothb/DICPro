"""
Configuration settings for the Document Integrity Protection System
Author: Okoth Bernard Wycliffe - 23/08325
Version: 1.0.0
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Document Integrity Protection System"
APP_VERSION = "1.0.0"
AUTHOR = "Okoth Bernard Wycliffe - 23/08325 (BISF)"

# File paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
KEYS_DIR = DATA_DIR / "keys"
LOGS_DIR = DATA_DIR / "logs"
SAMPLES_DIR = BASE_DIR / "samples"

# Ensure directories exist
for directory in [DATA_DIR, INPUT_DIR, OUTPUT_DIR, KEYS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Encryption settings
KEY_SIZE = 32  # AES-256 (256 bits = 32 bytes)
HASH_ALGORITHM = "sha256"
ENCRYPTION_MODE = "AES"
SALT_SIZE = 16  # 16 bytes for salt

# GUI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 400
THEME = "light"  # light or dark

# GUI Colors
COLORS = {
    "light": {
        "bg": "#ffffff",
        "fg": "#333333",
        "accent": "#007acc",
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "secondary": "#f8f9fa"
    },
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "accent": "#0099ff",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "secondary": "#404040"
    }
}

# File settings
SUPPORTED_TEXT_FORMATS = [".txt", ".docx", ".pdf", ".xlsx", ".xls", ".csv"]
SUPPORTED_IMAGE_FORMATS = [".png", ".jpg", ".jpeg", ".bmp"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB maximum file size

# Steganography settings
STEG_DELIMITER = "###INTEGRITY_DATA###"
STEG_END_MARKER = "###END_INTEGRITY###"
LSB_BITS = 1  # Number of LSBs to use for image steganography

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "app.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Verification settings
HASH_VERIFICATION_TIMEOUT = 30  # seconds
BATCH_PROCESSING_LIMIT = 100  # maximum files in batch

# Development settings
DEBUG = False
VERBOSE_LOGGING = False

# File extensions mapping
FILE_TYPE_MAPPING = {
    ".txt": "Text Document",
    ".docx": "Word Document", 
    ".pdf": "PDF Document",
    ".png": "PNG Image",
    ".jpg": "JPEG Image",
    ".jpeg": "JPEG Image",
    ".bmp": "Bitmap Image",
    ".xlsx": "Excel Workbook",
    ".xls": "Excel 97-2003 Workbook",
    ".csv": "CSV File"
}

# Default file names
DEFAULT_OUTPUT_SUFFIX = "_protected"
DEFAULT_KEY_FILE = "encryption.key"
DEFAULT_REPORT_FILE = "integrity_report.txt"

# Error messages
ERROR_MESSAGES = {
    "file_not_found": "The specified file could not be found.",
    "invalid_format": "Unsupported file format.",
    "file_too_large": f"File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB.",
    "encryption_failed": "Failed to encrypt the document hash.",
    "decryption_failed": "Failed to decrypt the document hash.",
    "verification_failed": "Document integrity verification failed.",
    "steganography_failed": "Failed to hide data in the document.",
    "extraction_failed": "Failed to extract hidden data from the document.",
    "key_generation_failed": "Failed to generate encryption key.",
    "invalid_key": "Invalid or corrupted encryption key."
}

# Success messages
SUCCESS_MESSAGES = {
    "protection_complete": "Document protection completed successfully.",
    "verification_passed": "Document integrity verified - no tampering detected.",
    "key_generated": "Encryption key generated successfully.",
    "batch_complete": "Batch processing completed successfully.",
    "file_saved": "File saved successfully."
}

# GUI Text Labels
GUI_LABELS = {
    "main_title": "Document Integrity Protection System",
    "select_file": "Select Document",
    "protect_document": "Protect Document",
    "verify_document": "Verify Document", 
    "generate_key": "Generate New Key",
    "batch_process": "Batch Process",
    "settings": "Settings",
    "help": "Help",
    "about": "About",
    "file_path": "File Path:",
    "status": "Status:",
    "progress": "Progress:",
    "results": "Results:"
}

# Application constants
APP_CONSTANTS = {
    "company": "University Project",
    "copyright": f"© 2024 {AUTHOR}",
    "license": "Academic Use Only",
    "contact": "2308325@students.kcau.ac.ke"
}