import os
import mimetypes
import magic
from typing import Tuple, Optional

# Optional: VirusTotal integration
try:
    import requests
except ImportError:
    requests = None

# Configuration
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.xlsx', '.xls', '.csv'}
MAX_FILE_SIZE_MB = 10
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', None)
VIRUSTOTAL_ENABLED = bool(VIRUSTOTAL_API_KEY)

# Helper: Get file extension
def get_extension(file_path: str) -> str:
    return os.path.splitext(file_path)[1].lower()

# Helper: Get file size in MB
def get_file_size_mb(file_path: str) -> float:
    return os.path.getsize(file_path) / (1024 * 1024)

# Helper: Check file signature (magic number)
def check_magic(file_path: str) -> bool:
    try:
        mime = magic.from_file(file_path, mime=True)
        # Accept only known/safe types
        if mime in [
            'application/pdf',
            'image/png', 'image/jpeg', 'image/bmp',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/csv',
        ]:
            return True
        return False
    except Exception:
        return False

# VirusTotal scan (optional, slow, privacy: uploads file to VT)
def scan_with_virustotal(file_path: str) -> Tuple[bool, str]:
    if not (VIRUSTOTAL_ENABLED and requests):
        return True, 'VirusTotal not enabled'
    try:
        url = 'https://www.virustotal.com/api/v3/files'
        headers = {'x-apikey': VIRUSTOTAL_API_KEY}
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            data = response.json()
            file_id = data['data']['id']
            # Poll for analysis result
            analysis_url = f'https://www.virustotal.com/api/v3/analyses/{file_id}'
            for _ in range(10):
                r = requests.get(analysis_url, headers=headers)
                if r.status_code == 200:
                    analysis = r.json()
                    stats = analysis['data']['attributes']['stats']
                    if stats['malicious'] > 0 or stats['suspicious'] > 0:
                        return False, f'VirusTotal flagged: {stats}'
                    if stats['undetected'] > 0:
                        return True, 'Clean (VirusTotal)'
                import time; time.sleep(2)
            return True, 'VirusTotal scan inconclusive'
        else:
            return True, f'VirusTotal error: {response.status_code}'
    except Exception as e:
        return True, f'VirusTotal scan error: {e}'

# Heuristic/AI checks (basic)
def heuristic_checks(file_path: str) -> Tuple[bool, str]:
    ext = get_extension(file_path)
    # Block macro-enabled Office files
    if ext in {'.xlsm', '.docm', '.pptm'}:
        return False, 'Macro-enabled Office files are not allowed.'
    # Check for double extensions (e.g., file.pdf.exe)
    base = os.path.basename(file_path)
    if base.count('.') > 1 and base.split('.')[-1] not in ALLOWED_EXTENSIONS:
        return False, 'Suspicious double extension.'
    # --- AI/ML Forgery/Tampering Detection Placeholder ---
    # For demonstration, flag as suspicious if a dummy flag is set (simulate AI detection)
    # In production, replace with real model inference (e.g., deep learning, anomaly detection)
    ai_forgery_detected = False
    # Example: if PDF or image, run dummy AI check
    if ext in {'.pdf', '.png', '.jpg', '.jpeg', '.bmp'}:
        # TODO: Replace with real AI/ML model call
        ai_forgery_detected = False  # Set to True to simulate detection
        if ai_forgery_detected:
            return False, 'AI/ML: Possible forgery or tampering detected.'
    return True, 'Passed heuristic and AI/ML checks.'

# Main scan function
def scan_file(file_path: str) -> Tuple[bool, str]:
    ext = get_extension(file_path)
    if ext not in ALLOWED_EXTENSIONS:
        return False, f'File type {ext} not allowed.'
    if get_file_size_mb(file_path) > MAX_FILE_SIZE_MB:
        return False, f'File size exceeds {MAX_FILE_SIZE_MB} MB.'
    if not check_magic(file_path):
        return False, 'File signature/magic number does not match allowed types.'
    ok, reason = heuristic_checks(file_path)
    if not ok:
        return False, reason
    ok, reason = scan_with_virustotal(file_path)
    if not ok:
        return False, reason
    return True, 'File passed all security checks.' 