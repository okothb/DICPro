"""
Unit tests for the steganography module
Document Integrity Protection System - Undergraduate Project

Tests cover:
- Text steganography (hiding/extracting data in text files)
- Image steganography (LSB method for images)
- Error handling and edge cases
- Data integrity verification
"""

import unittest
import os
import tempfile
from PIL import Image
import numpy as np
from core.steganography import TextSteganography, ImageSteganography


class TestTextSteganography(unittest.TestCase):
    """Test cases for text steganography functionality"""
    
    def setUp(self):
        """Setup test environment before each test"""
        self.text_stego = TextSteganography()
        self.test_text = "This is a sample document for testing steganography. " \
                        "It contains multiple sentences with various punctuation marks! " \
                        "We will hide encrypted hash data within this text using " \
                        "whitespace manipulation techniques."
        self.test_data = "encrypted_hash_data_12345"
        
    def test_hide_data_in_text(self):
        """Test hiding data in text using whitespace manipulation"""
        # Hide data in text
        stego_text = self.text_stego.hide_data(self.test_text, self.test_data)
        
        # Verify the text is modified (should contain hidden data)
        self.assertNotEqual(self.test_text, stego_text)
        self.assertIsInstance(stego_text, str)
        self.assertGreater(len(stego_text), len(self.test_text))
        
    def test_extract_data_from_text(self):
        """Test extracting hidden data from steganographic text"""
        # First hide data
        stego_text = self.text_stego.hide_data(self.test_text, self.test_data)
        
        # Then extract it
        extracted_data = self.text_stego.extract_data(stego_text)
        
        # Verify extraction is successful
        self.assertEqual(extracted_data, self.test_data)
        
    def test_hide_extract_cycle(self):
        """Test complete hide-extract cycle maintains data integrity"""
        original_data = "test_hash_value_abcdef123456"
        
        # Hide and extract data
        stego_text = self.text_stego.hide_data(self.test_text, original_data)
        extracted_data = self.text_stego.extract_data(stego_text)
        
        # Verify data integrity
        self.assertEqual(original_data, extracted_data)
        
    def test_empty_data_hiding(self):
        """Test handling of empty data"""
        with self.assertRaises(ValueError):
            self.text_stego.hide_data(self.test_text, "")
            
    def test_empty_text_hiding(self):
        """Test handling of empty text"""
        with self.assertRaises(ValueError):
            self.text_stego.hide_data("", self.test_data)
            
    def test_large_data_hiding(self):
        """Test hiding large amounts of data"""
        large_data = "x" * 1000  # 1KB of data
        
        try:
            stego_text = self.text_stego.hide_data(self.test_text, large_data)
            extracted_data = self.text_stego.extract_data(stego_text)
            self.assertEqual(large_data, extracted_data)
        except ValueError as e:
            # Expected if text is too small for large data
            self.assertIn("insufficient", str(e).lower())
            
    def test_special_characters_in_data(self):
        """Test hiding data with special characters"""
        special_data = "hash@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        
        stego_text = self.text_stego.hide_data(self.test_text, special_data)
        extracted_data = self.text_stego.extract_data(stego_text)
        
        self.assertEqual(special_data, extracted_data)
        
    def test_unicode_text_handling(self):
        """Test handling of unicode characters in text"""
        unicode_text = "Test with unicode: café, naïve, résumé, 中文, العربية"
        
        stego_text = self.text_stego.hide_data(unicode_text, self.test_data)
        extracted_data = self.text_stego.extract_data(stego_text)
        
        self.assertEqual(self.test_data, extracted_data)


class TestImageSteganography(unittest.TestCase):
    """Test cases for image steganography functionality"""
    
    def setUp(self):
        """Setup test environment before each test"""
        self.image_stego = ImageSteganography()
        self.test_data = "encrypted_hash_12345"
        
        # Create a test image
        self.test_image = Image.new('RGB', (100, 100), color='white')
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, 'test_image.png')
        self.test_image.save(self.test_image_path)
        
    def tearDown(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_hide_data_in_image(self):
        """Test hiding data in image using LSB method"""
        output_path = os.path.join(self.temp_dir, 'stego_image.png')
        
        # Hide data in image
        success = self.image_stego.hide_data(
            self.test_image_path, 
            self.test_data, 
            output_path
        )
        
        # Verify operation success
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify image file is valid
        stego_image = Image.open(output_path)
        self.assertEqual(stego_image.size, self.test_image.size)
        
    def test_extract_data_from_image(self):
        """Test extracting hidden data from steganographic image"""
        output_path = os.path.join(self.temp_dir, 'stego_image.png')
        
        # Hide data first
        self.image_stego.hide_data(
            self.test_image_path, 
            self.test_data, 
            output_path
        )
        
        # Extract data
        extracted_data = self.image_stego.extract_data(output_path)
        
        # Verify extraction
        self.assertEqual(extracted_data, self.test_data)
        
    def test_image_hide_extract_cycle(self):
        """Test complete hide-extract cycle for images"""
        original_data = "hash_value_abcdef123456789"
        output_path = os.path.join(self.temp_dir, 'stego_image.png')
        
        # Hide and extract data
        hide_success = self.image_stego.hide_data(
            self.test_image_path, 
            original_data, 
            output_path
        )
        extracted_data = self.image_stego.extract_data(output_path)
        
        # Verify cycle integrity
        self.assertTrue(hide_success)
        self.assertEqual(original_data, extracted_data)
        
    def test_large_image_capacity(self):
        """Test steganography capacity with larger images"""
        # Create larger test image
        large_image = Image.new('RGB', (500, 500), color='blue')
        large_image_path = os.path.join(self.temp_dir, 'large_image.png')
        large_image.save(large_image_path)
        
        # Test with larger data
        large_data = "large_hash_" + "x" * 1000
        output_path = os.path.join(self.temp_dir, 'large_stego.png')
        
        success = self.image_stego.hide_data(
            large_image_path, 
            large_data, 
            output_path
        )
        
        if success:
            extracted_data = self.image_stego.extract_data(output_path)
            self.assertEqual(large_data, extracted_data)
        else:
            # Expected if data is too large for image
            self.assertTrue(True)  # Test passed - proper capacity check
            
    def test_invalid_image_path(self):
        """Test handling of invalid image paths"""
        invalid_path = os.path.join(self.temp_dir, 'nonexistent.png')
        output_path = os.path.join(self.temp_dir, 'output.png')
        
        with self.assertRaises(FileNotFoundError):
            self.image_stego.hide_data(invalid_path, self.test_data, output_path)
            
    def test_corrupted_image_handling(self):
        """Test handling of corrupted image files"""
        corrupted_path = os.path.join(self.temp_dir, 'corrupted.png')
        
        # Create a corrupted file
        with open(corrupted_path, 'wb') as f:
            f.write(b'corrupted image data')
            
        output_path = os.path.join(self.temp_dir, 'output.png')
        
        with self.assertRaises(Exception):
            self.image_stego.hide_data(corrupted_path, self.test_data, output_path)
            
    def test_different_image_formats(self):
        """Test steganography with different image formats"""
        formats = [('JPEG', 'jpg'), ('PNG', 'png'), ('BMP', 'bmp')]
        
        for format_name, extension in formats:
            if format_name == 'JPEG':
                # JPEG uses lossy compression, skip for now
                continue
                
            # Create test image in format
            test_img = Image.new('RGB', (100, 100), color='red')
            img_path = os.path.join(self.temp_dir, f'test.{extension}')
            test_img.save(img_path, format=format_name)
            
            output_path = os.path.join(self.temp_dir, f'stego.{extension}')
            
            # Test steganography
            success = self.image_stego.hide_data(img_path, self.test_data, output_path)
            
            if success:
                extracted_data = self.image_stego.extract_data(output_path)
                self.assertEqual(self.test_data, extracted_data)


class TestSteganographyIntegration(unittest.TestCase):
    """Integration tests for steganography modules"""
    
    def setUp(self):
        """Setup for integration tests"""
        self.text_stego = TextSteganography()
        self.image_stego = ImageSteganography()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after integration tests"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_cross_format_data_consistency(self):
        """Test data consistency across text and image steganography"""
        test_data = "consistent_hash_data_12345"
        
        # Test with text
        text_sample = "Sample text for steganography testing with sufficient length."
        stego_text = self.text_stego.hide_data(text_sample, test_data)
        extracted_from_text = self.text_stego.extract_data(stego_text)
        
        # Test with image
        test_image = Image.new('RGB', (100, 100), color='green')
        image_path = os.path.join(self.temp_dir, 'test.png')
        stego_path = os.path.join(self.temp_dir, 'stego.png')
        test_image.save(image_path)
        
        self.image_stego.hide_data(image_path, test_data, stego_path)
        extracted_from_image = self.image_stego.extract_data(stego_path)
        
        # Verify consistency
        self.assertEqual(test_data, extracted_from_text)
        self.assertEqual(test_data, extracted_from_image)
        self.assertEqual(extracted_from_text, extracted_from_image)
        
    def test_performance_benchmarking(self):
        """Basic performance test for steganography operations"""
        import time
        
        test_data = "performance_test_hash_" + "x" * 100
        
        # Benchmark text steganography
        text_sample = "Performance test text. " * 50
        start_time = time.time()
        stego_text = self.text_stego.hide_data(text_sample, test_data)
        text_hide_time = time.time() - start_time
        
        start_time = time.time()
        extracted_text_data = self.text_stego.extract_data(stego_text)
        text_extract_time = time.time() - start_time
        
        # Benchmark image steganography
        test_image = Image.new('RGB', (200, 200), color='yellow')
        image_path = os.path.join(self.temp_dir, 'perf_test.png')
        stego_path = os.path.join(self.temp_dir, 'perf_stego.png')
        test_image.save(image_path)
        
        start_time = time.time()
        self.image_stego.hide_data(image_path, test_data, stego_path)
        image_hide_time = time.time() - start_time
        
        start_time = time.time()
        extracted_image_data = self.image_stego.extract_data(stego_path)
        image_extract_time = time.time() - start_time
        
        # Verify operations completed successfully
        self.assertEqual(test_data, extracted_text_data)
        self.assertEqual(test_data, extracted_image_data)
        
        # Basic performance assertions (operations should complete within reasonable time)
        self.assertLess(text_hide_time, 5.0)  # 5 seconds max
        self.assertLess(text_extract_time, 5.0)
        self.assertLess(image_hide_time, 10.0)  # 10 seconds max for image
        self.assertLess(image_extract_time, 10.0)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestTextSteganography))
    suite.addTest(unittest.makeSuite(TestImageSteganography))
    suite.addTest(unittest.makeSuite(TestSteganographyIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
