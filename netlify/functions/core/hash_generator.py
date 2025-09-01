"""
Simplified Hash Generator for Netlify Functions
"""

import hashlib
import os
import csv
import openpyxl


class HashGenerator:
    """Simplified hash generator for serverless environment"""
    
    def __init__(self):
        self.buffer_size = 65536
    
    def generate_file_hash(self, file_path: str) -> str:
        """Generate SHA-256 hash for a file"""
        try:
            if not os.path.exists(file_path):
                return None
                
            sha256_hash = hashlib.sha256()
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in [".xlsx", ".xls"]:
                # Hash Excel content
                try:
                    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                    for ws in wb.worksheets:
                        for row in ws.iter_rows(values_only=True):
                            for cell in row:
                                if cell is not None:
                                    sha256_hash.update(str(cell).encode("utf-8"))
                    wb.close()
                except Exception:
                    # Fallback to file hash
                    with open(file_path, "rb") as f:
                        while chunk := f.read(self.buffer_size):
                            sha256_hash.update(chunk)
            elif ext == ".csv":
                # Hash CSV content
                try:
                    with open(file_path, "r", encoding="utf-8") as csvfile:
                        reader = csv.reader(csvfile)
                        for row in reader:
                            sha256_hash.update(",".join(row).encode("utf-8"))
                except Exception:
                    # Fallback to file hash
                    with open(file_path, "rb") as f:
                        while chunk := f.read(self.buffer_size):
                            sha256_hash.update(chunk)
            else:
                # Standard file hash
                with open(file_path, "rb") as f:
                    while chunk := f.read(self.buffer_size):
                        sha256_hash.update(chunk)
            
            return sha256_hash.hexdigest()
            
        except Exception as e:
            print(f"Error generating hash: {e}")
            return None