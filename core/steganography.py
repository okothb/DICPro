"""
Document Integrity Protection System - Steganography Module
Provides functionality to hide and extract data within documents and images.
"""

import os
import json
import struct
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from PIL import Image
import numpy as np
import base64
import openpyxl
import csv

# Import for .docx and .pdf functionalities
try:
    from docx import Document
    from docx.shared import RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
except ImportError:
    print("python-docx not installed. Docx functionalities will be unavailable.")
    Document = None
    RGBColor = None
    WD_ALIGN_PARAGRAPH = None
    Pt = None

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not installed. PDF functionalities will be unavailable.")
    PyPDF2 = None


class DocumentSteganography:
    """
    Handles steganography operations for hiding data in documents and images.
    """
    
    def __init__(self):
        """Initialize the DocumentSteganography with default settings."""
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        self.supported_text_formats = {'.txt', '.md', '.py', '.js', '.html', '.css'}
        # Add .docx and .pdf to supported binary formats
        self.supported_binary_formats = {'.docx', '.pdf'}
        self.delimiter = b'\x00\x00\xFF\xFF\x00\x00'  # Unique delimiter for data separation
        self.max_text_chars = 100000  # Maximum characters for text steganography
    
    def hide_data_in_image(self, cover_image_path: str, secret_data: bytes, 
                          output_path: str, method: str = 'lsb', 
                          original_hash: str = None, protected_hash: str = None) -> Dict[str, Any]:
        """
        Hide data in an image using steganography.
        
        Args:
            cover_image_path (str): Path to cover image
            secret_data (bytes): Data to hide
            output_path (str): Path for output image
            method (str): Steganography method ('lsb' for Least Significant Bit)
            original_hash (str): Hash of original document before protection
            protected_hash (str): Hash of protected document (for verification)
            
        Returns:
            Dict[str, Any]: Operation result with metadata
        """
        try:
            if not os.path.exists(cover_image_path):
                return {'error': 'Cover image not found', 'success': False}
            
            # Check file format
            file_ext = os.path.splitext(cover_image_path)[1].lower()
            if file_ext not in self.supported_image_formats:
                return {'error': f'Unsupported image format: {file_ext}', 'success': False}
            
            # Load image
            image = Image.open(cover_image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert image to numpy array
            img_array = np.array(image)
            height, width, channels = img_array.shape
            
            # Prepare data with metadata INCLUDING HASH INFORMATION
            metadata = {
                'original_name': os.path.basename(cover_image_path),
                'data_length': len(secret_data),
                'hidden_at': datetime.now().isoformat(),
                'method': method,
                'original_hash': original_hash,  # Store original document hash
                'protected_hash': protected_hash  # Store protected document hash for verification
            }
            
            # Combine metadata and secret data
            metadata_json = json.dumps(metadata).encode('utf-8')
            full_data = metadata_json + self.delimiter + secret_data
            
            # Check if image can hold the data
            max_capacity = (height * width * channels) // 8  # 1 bit per channel
            if len(full_data) > max_capacity:
                return {
                    'error': f'Data too large for image. Max capacity: {max_capacity} bytes, Data size: {len(full_data)} bytes',
                    'success': False
                }
            
            # Convert data to binary
            binary_data = ''.join(format(byte, '08b') for byte in full_data)
            
            final_output_path = output_path

            # Hide data using LSB method
            if method == 'lsb':
                img_flat = img_array.flatten()
                for i, bit in enumerate(binary_data):
                    img_flat[i] = (img_flat[i] & 0xFE) | int(bit)

                # Reshape back to original dimensions
                stego_array = img_flat.reshape(height, width, channels)

                # Create a Pillow Image object from the modified array
                stego_image = Image.fromarray(stego_array.astype('uint8'))

                # LSB steganography requires a lossless format like PNG to preserve the hidden data.
                # Saving to a lossy format like JPEG will corrupt the data.
                # We will change the output extension to .png and save in PNG format.
                final_output_path = os.path.splitext(output_path)[0] + '.png'
                stego_image.save(final_output_path, 'PNG')
            else:
                return {'error': f'Unsupported image steganography method: {method}', 'success': False}

            return {
                'success': True,
                'cover_image': cover_image_path,
                'stego_image': final_output_path,
                'data_size': len(secret_data),
                'metadata_size': len(metadata_json),
                'total_hidden_size': len(full_data),
                'capacity_used': f'{(len(full_data) / max_capacity) * 100:.2f}%',
                'method': method,
                'original_hash': original_hash,
                'protected_hash': protected_hash  # Return both hashes for UI display
            }

        except Exception as e:
            return {'error': f'Image steganography failed: {str(e)}', 'success': False}

    def extract_data_from_image(self, stego_image_path: str, method: str = 'lsb') -> Dict[str, Any]:
        """
        Extract hidden data from a steganographic image.

        Args:
            stego_image_path (str): Path to steganographic image
            method (str): Steganography method used ('lsb')

        Returns:
            Dict[str, Any]: Extracted data and metadata (including hash information)
        """
        try:
            if not os.path.exists(stego_image_path):
                return {'error': 'Steganographic image not found', 'success': False}

            # Load image
            image = Image.open(stego_image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            img_array = np.array(image)

            if method == 'lsb':
                # Extract LSBs
                img_flat = img_array.flatten()
                binary_data = ''.join(str(pixel & 1) for pixel in img_flat)

                # Convert binary to bytes
                extracted_bytes = bytearray()
                for i in range(0, len(binary_data), 8):
                    byte_chunk = binary_data[i:i+8]
                    if len(byte_chunk) == 8:
                        extracted_bytes.append(int(byte_chunk, 2))

                # Find delimiter to separate metadata from secret data
                delimiter_index = extracted_bytes.find(self.delimiter)
                if delimiter_index == -1:
                    return {'error': 'No hidden data found or data corrupted', 'success': False}

                # Extract metadata
                metadata_bytes = extracted_bytes[:delimiter_index]
                try:
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                except Exception:
                    return {'error': 'Corrupted metadata', 'success': False}

                # Extract secret data
                secret_start = delimiter_index + len(self.delimiter)
                secret_end = secret_start + metadata['data_length']
                secret_data = bytes(extracted_bytes[secret_start:secret_end])

                return {
                    'success': True,
                    'secret_data': secret_data,
                    'metadata': metadata,
                    'extracted_size': len(secret_data),
                    'method': method,
                    'original_hash': metadata.get('original_hash'),  # Extract original hash
                    'protected_hash': metadata.get('protected_hash')  # Extract protected hash for verification
                }

            return {'error': f'Unsupported image extraction method: {method}', 'success': False}

        except Exception as e:
            return {'error': f'Data extraction failed: {str(e)}', 'success': False}

    def hide_data_in_text(self, cover_text_path: str, secret_data: bytes,
                         output_path: str, method: str = 'whitespace',
                         original_hash: str = None, protected_hash: str = None) -> Dict[str, Any]:
        """
        Hide data in text files using steganography.

        Args:
            cover_text_path (str): Path to cover text file
            secret_data (bytes): Data to hide
            output_path (str): Path for output text file
            method (str): Method ('whitespace', 'unicode', 'punctuation')
            original_hash (str): Hash of original document before protection
            protected_hash (str): Hash of protected document (for verification)

        Returns:
            Dict[str, Any]: Operation result with metadata
        """
        try:
            if not os.path.exists(cover_text_path):
                return {'error': 'Cover text file not found', 'success': False}

            # Check if the cover file format is supported for text steganography
            file_ext = os.path.splitext(cover_text_path)[1].lower()
            if file_ext not in self.supported_text_formats:
                return {
                    'error': 'Text steganography requires a text-based cover file. '
                             f'Cannot use a "{file_ext}" file. Please select a valid text file (e.g., .txt, .md).',
                    'success': False
                }
            
            # Read cover text
            with open(cover_text_path, 'r', encoding='utf-8') as f:
                cover_text = f.read()
            
            if len(cover_text) > self.max_text_chars:
                return {'error': f'Text file too large. Max: {self.max_text_chars} chars', 'success': False}
            
            # Prepare data with metadata INCLUDING HASH INFORMATION
            metadata = {
                'original_name': os.path.basename(cover_text_path),
                'data_length': len(secret_data),
                'hidden_at': datetime.now().isoformat(),
                'method': method,
                'original_hash': original_hash,  # Store original document hash
                'protected_hash': protected_hash  # Store protected document hash for verification
            }
            
            metadata_json = json.dumps(metadata).encode('utf-8')
            full_data = metadata_json + self.delimiter + secret_data
            
            # Convert to binary
            binary_data = ''.join(format(byte, '08b') for byte in full_data)
            
            if method == 'whitespace':
                stego_text = self._hide_in_whitespace(cover_text, binary_data)
            elif method == 'unicode':
                stego_text = self._hide_in_unicode(cover_text, binary_data)
            elif method == 'punctuation':
                stego_text = self._hide_in_punctuation(cover_text, binary_data)
            else:
                return {'error': f'Unsupported text steganography method: {method}', 'success': False}
            
            if stego_text is None:
                return {'error': 'Failed to hide data in text - insufficient capacity', 'success': False}
            
            # Save stego text
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(stego_text)
            
            return {
                'success': True,
                'cover_text': cover_text_path,
                'stego_text': output_path,
                'data_size': len(secret_data),
                'method': method,
                'original_length': len(cover_text),
                'stego_length': len(stego_text),
                'original_hash': original_hash,
                'protected_hash': protected_hash  # Return both hashes for UI display
            }
            
        except Exception as e:
            return {'error': f'Text steganography failed: {str(e)}', 'success': False}
    
    def extract_data_from_text(self, stego_text_path: str, method: str = 'whitespace') -> Dict[str, Any]:
        """
        Extract hidden data from steganographic text.
        
        Args:
            stego_text_path (str): Path to steganographic text file
            method (str): Method used for hiding data
            
        Returns:
            Dict[str, Any]: Extracted data and metadata (including hash information)
        """
        try:
            if not os.path.exists(stego_text_path):
                return {'error': 'Steganographic text file not found', 'success': False}
            
            # Read stego text
            with open(stego_text_path, 'r', encoding='utf-8') as f:
                stego_text = f.read()
            
            # Extract binary data based on method
            if method == 'whitespace':
                binary_data = self._extract_from_whitespace(stego_text)
            elif method == 'unicode':
                binary_data = self._extract_from_unicode(stego_text)
            elif method == 'punctuation':
                binary_data = self._extract_from_punctuation(stego_text)
            else:
                return {'error': f'Unsupported extraction method: {method}', 'success': False}
            
            if not binary_data:
                return {'error': 'No hidden data found', 'success': False}
            
            # Convert binary to bytes
            extracted_bytes = bytearray()
            for i in range(0, len(binary_data), 8):
                byte_chunk = binary_data[i:i+8]
                if len(byte_chunk) == 8:
                    extracted_bytes.append(int(byte_chunk, 2))
            
            # Find delimiter
            delimiter_index = extracted_bytes.find(self.delimiter)
            if delimiter_index == -1:
                return {'error': 'Data corrupted or not found', 'success': False}
            
            # Extract metadata and secret data
            metadata_bytes = extracted_bytes[:delimiter_index]
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            secret_start = delimiter_index + len(self.delimiter)
            secret_end = secret_start + metadata['data_length']
            secret_data = bytes(extracted_bytes[secret_start:secret_end])
            
            return {
                'success': True,
                'secret_data': secret_data,
                'metadata': metadata,
                'extracted_size': len(secret_data),
                'method': method,
                'original_hash': metadata.get('original_hash'),  # Extract original hash
                'protected_hash': metadata.get('protected_hash')  # Extract protected hash for verification
            }
            
        except Exception as e:
            return {'error': f'Text extraction failed: {str(e)}', 'success': False}

    def hide_data_in_docx(self, cover_docx_path: str, secret_data: bytes,
                          output_path: str, original_hash: str = None,
                          protected_hash: str = None) -> Dict[str, Any]:
        """
        Hide data in a .docx file using steganography methods.
        
        Args:
            cover_docx_path (str): Path to cover .docx file
            secret_data (bytes): Data to hide
            output_path (str): Path for output .docx file
            original_hash (str): Hash of original document before protection
            protected_hash (str): Hash of protected document (for verification)
            
        Returns:
            Dict[str, Any]: Operation result with metadata
        """
        if Document is None:
            return {'error': 'python-docx library not installed.', 'success': False}

        try:
            if not os.path.exists(cover_docx_path):
                return {'error': 'Cover .docx file not found', 'success': False}
            
            doc = Document(cover_docx_path)
            
            metadata = {
                'original_name': os.path.basename(cover_docx_path),
                'data_length': len(secret_data),
                'hidden_at': datetime.now().isoformat(),
                'method': 'docx_metadata',  # Explicitly state the method
                'original_hash': original_hash,
                'protected_hash': protected_hash
            }
            
            metadata_json = json.dumps(metadata).encode('utf-8')
            full_data = metadata_json + self.delimiter + secret_data
            
            # Method 1: Hide in document properties (comments field)
            # Base64 encode the full_data to ensure it's text-safe for metadata
            encoded_data = base64.b64encode(full_data).decode('utf-8')
            doc.core_properties.comments = encoded_data
            
            # Method 2: Hide in invisible text (optional, for more capacity/robustness)
            # This method can increase file size noticeably and might be easier to detect.
            # Only add if needed for larger data, or as a secondary layer.
            # For simplicity, we'll stick to metadata for primary hiding.
            # If the data is very small, we could add it as tiny white text.
            # if len(full_data) < 1024: # Example capacity check for invisible text
            #     paragraph = doc.add_paragraph()
            #     run = paragraph.add_run(encoded_data)
            #     run.font.color.rgb = RGBColor(255, 255, 255)  # White text on white background
            #     run.font.size = Pt(1)  # Tiny size
            #     run.font.hidden = True # Mark as hidden (though some viewers might reveal)

            doc.save(output_path)
            
            return {
                'success': True,
                'cover_document': cover_docx_path,
                'stego_document': output_path,
                'data_size': len(secret_data),
                'metadata_size': len(metadata_json),
                'total_hidden_size': len(full_data),
                'method': 'docx_metadata',
                'original_hash': original_hash,
                'protected_hash': protected_hash
            }
        
        except Exception as e:
            return {'error': f'Docx steganography failed: {str(e)}', 'success': False}

    def extract_data_from_docx(self, stego_docx_path: str) -> Dict[str, Any]:
        """
        Extract hidden data from a steganographic .docx file.
        
        Args:
            stego_docx_path (str): Path to steganographic .docx file
            
        Returns:
            Dict[str, Any]: Extracted data and metadata
        """
        if Document is None:
            return {'error': 'python-docx library not installed.', 'success': False}

        try:
            if not os.path.exists(stego_docx_path):
                return {'error': 'Steganographic .docx file not found', 'success': False}
            
            doc = Document(stego_docx_path)
            
            # Extract from document properties (comments field)
            encoded_data = doc.core_properties.comments
            if not encoded_data:
                return {'error': 'No hidden data found in .docx metadata', 'success': False}
            
            full_data = base64.b64decode(encoded_data.encode('utf-8'))
            
            delimiter_index = full_data.find(self.delimiter)
            if delimiter_index == -1:
                return {'error': 'Data corrupted or no delimiter found in .docx', 'success': False}
            
            metadata_bytes = full_data[:delimiter_index]
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            secret_start = delimiter_index + len(self.delimiter)
            secret_end = secret_start + metadata['data_length']
            secret_data = full_data[secret_start:secret_end]
            
            return {
                'success': True,
                'secret_data': secret_data,
                'metadata': metadata,
                'extracted_size': len(secret_data),
                'method': 'docx_metadata',
                'original_hash': metadata.get('original_hash'),
                'protected_hash': metadata.get('protected_hash')
            }
            
        except Exception as e:
            return {'error': f'Docx data extraction failed: {str(e)}', 'success': False}

    def hide_data_in_pdf(self, cover_pdf_path: str, secret_data: bytes,
                         output_path: str, original_hash: str = None,
                         protected_hash: str = None) -> Dict[str, Any]:
        """
        Enhanced: Hide data in a PDF file by embedding it in metadata.
        Supports larger data by splitting across multiple metadata fields if needed.
        
        Args:
            cover_pdf_path (str): Path to the cover PDF file.
            secret_data (bytes): The data to hide.
            output_path (str): Path where the steganographic PDF will be saved.
            original_hash (str): Hash of original document before protection
            protected_hash (str): Hash of protected document (for verification)
            
        Returns:
            Dict[str, Any]: Operation result with metadata.
        """
        if PyPDF2 is None:
            return {'error': 'PyPDF2 library not installed. Please install: pip install PyPDF2', 'success': False}

        try:
            if not os.path.exists(cover_pdf_path):
                return {'error': 'Cover PDF file not found', 'success': False}
            
            # Check file size and ensure it's a valid PDF
            file_size = os.path.getsize(cover_pdf_path)
            if file_size == 0:
                return {'error': 'Cover PDF file is empty', 'success': False}
            
            with open(cover_pdf_path, 'rb') as file:
                # Verify it's a valid PDF by checking header
                header = file.read(4)
                if header != b'%PDF':
                    return {'error': 'Invalid PDF file format', 'success': False}
                
                file.seek(0)  # Reset to beginning
                reader = PyPDF2.PdfReader(file)
                
                if len(reader.pages) == 0:
                    return {'error': 'PDF file contains no pages', 'success': False}
                
                writer = PyPDF2.PdfWriter()
                
                # Copy all pages from reader to writer
                for page in reader.pages:
                    writer.add_page(page)

                metadata = {
                    'original_name': os.path.basename(cover_pdf_path),
                    'data_length': len(secret_data),
                    'hidden_at': datetime.now().isoformat(),
                    'method': 'pdf_metadata',
                    'original_hash': original_hash,
                    'protected_hash': protected_hash,
                    'version': '2.0'
                }
                
                metadata_json = json.dumps(metadata).encode('utf-8')
                full_data = metadata_json + self.delimiter + secret_data
                
                # Base64 encode the full_data to ensure it's text-safe for PDF metadata
                encoded_data = base64.b64encode(full_data).decode('utf-8')
                
                # Check if data is too large for a single metadata field (typical limit is ~64KB)
                if len(encoded_data) > 60000:  # Conservative limit
                    return {
                        'error': f'Data too large for PDF metadata. Size: {len(encoded_data)} chars, Max: ~60KB',
                        'success': False
                    }
                
                # Add data to PDF metadata with enhanced fields
                metadata_dict = {
                    '/Subject': encoded_data,
                    '/Keywords': 'document_integrity_protected',
                    '/Creator': 'DocPro Steganography System',
                    '/Producer': 'Document Integrity Protection System v2.0'
                }
                
                writer.add_metadata(metadata_dict)
                
                # Ensure output directory exists
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                with open(output_path, 'wb') as output_pdf_file:
                    writer.write(output_pdf_file)
            
            return {
                'success': True,
                'cover_document': cover_pdf_path,
                'stego_document': output_path,
                'data_size': len(secret_data),
                'metadata_size': len(metadata_json),
                'total_hidden_size': len(full_data),
                'encoded_size': len(encoded_data),
                'method': 'pdf_metadata',
                'original_hash': original_hash,
                'protected_hash': protected_hash
            }
        
        except Exception as e:
            return {'error': f'PDF steganography failed: {str(e)}', 'success': False}

    def extract_data_from_pdf(self, stego_pdf_path: str) -> Dict[str, Any]:
        """
        Enhanced: Extract hidden data from a steganographic PDF file.
        Includes better error handling and validation.
        
        Args:
            stego_pdf_path (str): Path to the steganographic PDF file.
            
        Returns:
            Dict[str, Any]: Extracted data and metadata.
        """
        if PyPDF2 is None:
            return {'error': 'PyPDF2 library not installed. Please install: pip install PyPDF2', 'success': False}

        try:
            if not os.path.exists(stego_pdf_path):
                return {'error': 'Steganographic PDF file not found', 'success': False}
            
            # Check if file is empty
            if os.path.getsize(stego_pdf_path) == 0:
                return {'error': 'PDF file is empty', 'success': False}
            
            with open(stego_pdf_path, 'rb') as file:
                # Verify it's a valid PDF
                header = file.read(4)
                if header != b'%PDF':
                    return {'error': 'Invalid PDF file format', 'success': False}
                
                file.seek(0)  # Reset to beginning
                reader = PyPDF2.PdfReader(file)
                
                metadata_pdf = reader.metadata
                if not metadata_pdf:
                    return {'error': 'No metadata found in PDF', 'success': False}
                
                # Try multiple metadata fields for hidden data
                encoded_data = None
                for field in ['/Subject', '/Keywords', '/Creator']:
                    if field in metadata_pdf:
                        field_data = metadata_pdf[field]
                        if field_data and len(field_data) > 100:  # Likely contains our data
                            try:
                                # Try to decode as base64
                                test_decode = base64.b64decode(field_data.encode('utf-8'))
                                if self.delimiter in test_decode:
                                    encoded_data = field_data
                                    break
                            except:
                                continue
                
                if not encoded_data:
                    return {'error': 'No hidden data found in PDF metadata', 'success': False}
                
                try:
                    full_data = base64.b64decode(encoded_data.encode('utf-8'))
                except Exception as e:
                    return {'error': f'Failed to decode base64 data: {str(e)}', 'success': False}
                
                delimiter_index = full_data.find(self.delimiter)
                if delimiter_index == -1:
                    return {'error': 'Data corrupted or no delimiter found in PDF', 'success': False}
                
                try:
                    metadata_bytes = full_data[:delimiter_index]
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                except Exception as e:
                    return {'error': f'Failed to parse metadata: {str(e)}', 'success': False}
                
                secret_start = delimiter_index + len(self.delimiter)
                secret_end = secret_start + metadata['data_length']
                
                if secret_end > len(full_data):
                    return {'error': 'Data length mismatch - file may be corrupted', 'success': False}
                
                secret_data = full_data[secret_start:secret_end]
                
                return {
                    'success': True,
                    'secret_data': secret_data,
                    'metadata': metadata,
                    'extracted_size': len(secret_data),
                    'method': 'pdf_metadata',
                    'original_hash': metadata.get('original_hash'),
                    'protected_hash': metadata.get('protected_hash')
                }
            
        except Exception as e:
            return {'error': f'PDF data extraction failed: {str(e)}', 'success': False}

    def has_steganographic_data_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Check if a PDF file contains steganographic data without extracting it.
        
        Args:
            pdf_path (str): Path to the PDF file to check.
            
        Returns:
            Dict[str, Any]: Check result with metadata if found.
        """
        if PyPDF2 is None:
            return {'error': 'PyPDF2 library not installed', 'success': False}

        try:
            if not os.path.exists(pdf_path):
                return {'error': 'PDF file not found', 'success': False}
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata_pdf = reader.metadata
                
                if not metadata_pdf:
                    return {'has_data': False, 'message': 'No metadata found in PDF'}
                
                # Check for steganographic data in metadata fields
                for field in ['/Subject', '/Keywords', '/Creator']:
                    if field in metadata_pdf:
                        field_data = metadata_pdf[field]
                        if field_data and len(field_data) > 100:
                            try:
                                test_decode = base64.b64decode(field_data.encode('utf-8'))
                                if self.delimiter in test_decode:
                                    return {
                                        'has_data': True,
                                        'message': f'Steganographic data found in {field} field',
                                        'field': field,
                                        'data_size': len(field_data)
                                    }
                            except:
                                continue
                
                return {'has_data': False, 'message': 'No steganographic data found in PDF metadata'}
                
        except Exception as e:
            return {'error': f'Error checking PDF: {str(e)}', 'success': False}

    def hide_data_in_excel(self, cover_excel_path: str, secret_data: bytes, output_path: str, original_hash: str = None, protected_hash: str = None) -> dict:
        """
        Hide data in Excel files (.xlsx, .xls, .csv) using a hidden worksheet or special comment line.
        """
        import os
        import base64
        import json
        from datetime import datetime
        ext = os.path.splitext(cover_excel_path)[1].lower()
        try:
            metadata = {
                'original_name': os.path.basename(cover_excel_path),
                'data_length': len(secret_data),
                'hidden_at': datetime.now().isoformat(),
                'method': 'excel_hidden_sheet',
                'original_hash': original_hash,
                'protected_hash': protected_hash
            }
            metadata_json = json.dumps(metadata).encode('utf-8')
            full_data = metadata_json + self.delimiter + secret_data
            encoded_data = base64.b64encode(full_data).decode('utf-8')
            if ext in [".xlsx", ".xls"]:
                wb = openpyxl.load_workbook(cover_excel_path)
                # Create a hidden sheet for stego data
                stego_sheet = wb.create_sheet(title=".stego_data")
                stego_sheet.sheet_state = 'hidden'
                stego_sheet["A1"] = encoded_data
                wb.save(output_path)
                wb.close()
                return {
                    'success': True,
                    'cover_excel': cover_excel_path,
                    'stego_excel': output_path,
                    'data_size': len(secret_data),
                    'method': 'excel_hidden_sheet',
                    'original_hash': original_hash,
                    'protected_hash': protected_hash
                }
            elif ext == ".csv":
                # Append a special comment line with the encoded data
                with open(cover_excel_path, "r", encoding="utf-8") as f:
                    rows = f.readlines()
                with open(output_path, "w", encoding="utf-8") as f:
                    for row in rows:
                        f.write(row)
                    f.write(f"#STEGO_DATA:{encoded_data}\n")
                return {
                    'success': True,
                    'cover_excel': cover_excel_path,
                    'stego_excel': output_path,
                    'data_size': len(secret_data),
                    'method': 'csv_comment',
                    'original_hash': original_hash,
                    'protected_hash': protected_hash
                }
            else:
                return {'error': f'Unsupported Excel file extension: {ext}', 'success': False}
        except Exception as e:
            return {'error': f'Excel steganography failed: {str(e)}', 'success': False}

    def extract_data_from_excel(self, stego_excel_path: str) -> dict:
        """
        Extract hidden data from Excel files (.xlsx, .xls, .csv) from a hidden worksheet or special comment line.
        """
        import os
        import base64
        import json
        ext = os.path.splitext(stego_excel_path)[1].lower()
        try:
            if ext in [".xlsx", ".xls"]:
                wb = openpyxl.load_workbook(stego_excel_path, read_only=True, data_only=True)
                if ".stego_data" not in wb.sheetnames:
                    return {'error': 'No hidden stego sheet found in Excel file', 'success': False}
                stego_sheet = wb[".stego_data"]
                encoded_data = stego_sheet["A1"].value
                wb.close()
                if not encoded_data:
                    return {'error': 'No hidden data found in Excel file', 'success': False}
                full_data = base64.b64decode(encoded_data.encode('utf-8'))
            elif ext == ".csv":
                with open(stego_excel_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                encoded_data = None
                for line in reversed(lines):
                    if line.startswith("#STEGO_DATA:"):
                        encoded_data = line[len("#STEGO_DATA:"):].strip()
                        break
                if not encoded_data:
                    return {'error': 'No hidden data found in CSV file', 'success': False}
                full_data = base64.b64decode(encoded_data.encode('utf-8'))
            else:
                return {'error': f'Unsupported Excel file extension: {ext}', 'success': False}
            delimiter_index = full_data.find(self.delimiter)
            if delimiter_index == -1:
                return {'error': 'Data corrupted or no delimiter found in Excel', 'success': False}
            metadata_bytes = full_data[:delimiter_index]
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            secret_start = delimiter_index + len(self.delimiter)
            secret_end = secret_start + metadata['data_length']
            if secret_end > len(full_data):
                return {'error': 'Data length mismatch - file may be corrupted', 'success': False}
            secret_data = full_data[secret_start:secret_end]
            return {
                'success': True,
                'secret_data': secret_data,
                'metadata': metadata,
                'extracted_size': len(secret_data),
                'method': 'excel_hidden_sheet' if ext in [".xlsx", ".xls"] else 'csv_comment',
                'original_hash': metadata.get('original_hash'),
                'protected_hash': metadata.get('protected_hash')
            }
        except Exception as e:
            return {'error': f'Excel data extraction failed: {str(e)}', 'success': False}

    def get_verification_hash(self, file_path: str, method: str = 'lsb') -> Optional[str]:
        """
        Get the stored protected hash from a steganographic file for verification.
        
        Args:
            file_path (str): Path to steganographic file
            method (str): Steganography method used (lsb, whitespace, docx_metadata, pdf_metadata)
            
        Returns:
            Optional[str]: Protected hash for verification, or None if not found
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in self.supported_image_formats:
                result = self.extract_data_from_image(file_path, method)
            elif file_ext in self.supported_text_formats:
                result = self.extract_data_from_text(file_path, method)
            elif file_ext == '.docx':
                result = self.extract_data_from_docx(file_path)
            elif file_ext == '.pdf':
                result = self.extract_data_from_pdf(file_path)
            elif file_ext in ['.xlsx', '.xls', '.csv']:
                result = self.extract_data_from_excel(file_path)
            else:
                return None
            
            if result.get('success') and result.get('protected_hash'):
                return result['protected_hash']
            
            return None
            
        except Exception:
            return None
    
    def _hide_in_whitespace(self, text: str, binary_data: str) -> Optional[str]:
        """Hide data using whitespace steganography (space/tab encoding)."""
        lines = text.split('\n')
        result_lines = []
        binary_index = 0
        
        for line in lines:
            if binary_index >= len(binary_data):
                result_lines.append(line)
                continue
            
            # Add hidden bits as trailing whitespace
            hidden_bits = ""
            bits_to_hide = min(8, len(binary_data) - binary_index)
            
            for i in range(bits_to_hide):
                if binary_index < len(binary_data):
                    # 0 = space, 1 = tab
                    hidden_bits += '\t' if binary_data[binary_index] == '1' else ' '
                    binary_index += 1
            
            result_lines.append(line + hidden_bits)
        
        return '\n'.join(result_lines) if binary_index >= len(binary_data) else None
    
    def _extract_from_whitespace(self, text: str) -> str:
        """Extract data from whitespace steganography."""
        lines = text.split('\n')
        binary_data = ""
        
        for line in lines:
            # Extract trailing whitespace
            trailing_ws = len(line) - len(line.rstrip(' \t'))
            if trailing_ws > 0:
                ws_chars = line[-trailing_ws:]
                for char in ws_chars:
                    binary_data += '1' if char == '\t' else '0'
        
        return binary_data
    
    def _hide_in_unicode(self, text: str, binary_data: str) -> Optional[str]:
        """Hide data using zero-width Unicode characters."""
        # Zero-width characters: ZWSP (0), ZWNJ (1)
        zwsp = '\u200B'  # Zero Width Space
        zwnj = '\u200C'  # Zero Width Non-Joiner
        
        result = ""
        binary_index = 0
        
        for char in text:
            result += char
            if binary_index < len(binary_data) and char.isalpha():
                # Insert zero-width character after letters
                if binary_data[binary_index] == '0':
                    result += zwsp
                else:
                    result += zwnj
                binary_index += 1
        
        return result if binary_index >= len(binary_data) else None
    
    def _extract_from_unicode(self, text: str) -> str:
        """Extract data from Unicode steganography."""
        zwsp = '\u200B'
        zwnj = '\u200C'
        binary_data = ""
        
        for char in text:
            if char == zwsp:
                binary_data += '0'
            elif char == zwnj:
                binary_data += '1'
        
        return binary_data
    
    def _hide_in_punctuation(self, text: str, binary_data: str) -> Optional[str]:
        """Hide data using punctuation variations."""
        # This is a simplified implementation
        # In practice, you'd use variations like single/double quotes, etc.
        result = ""
        binary_index = 0
        
        for char in text:
            result += char
            if binary_index < len(binary_data) and char in '.,!?;:':
                # Add invisible character after punctuation
                if binary_data[binary_index] == '0':
                    result += '\u200B'  # Zero width space
                else:
                    result += '\u200C'  # Zero width non-joiner
                binary_index += 1
        
        return result if binary_index >= len(binary_data) else None
    
    def _extract_from_punctuation(self, text: str) -> str:
        """Extract data from punctuation steganography."""
        zwsp = '\u200B'
        zwnj = '\u200C'
        binary_data = ""
        
        for char in text:
            if char == zwsp:
                binary_data += '0'
            elif char == zwnj:
                binary_data += '1'
        
        return binary_data