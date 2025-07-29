#!/usr/bin/env python3
"""
Test script for batch file selection, drag-and-drop, and output folder picker in the web app.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Testing batch file selection, drag-and-drop, and output folder picker...")
    try:
        from web_app import DocumentProtectionWebApp
        import flet as ft
        app = DocumentProtectionWebApp()
        # Simulate page
        class MockPage:
            def __init__(self):
                self.title = ""
                self.window_width = 1200
                self.window_height = 800
                self.padding = 20
                self.spacing = 20
                self.favicon = None
                self.overlay = []
                self.views = []
                self.app_bar = None
                self.snack_bar = None
                self.on_route_change = None
            def show_snack_bar(self, sb):
                print(f"[SnackBar] {sb.content.value}")
            def update(self):
                pass
        page = MockPage()
        app.main(page)
        # Simulate output folder selection
        class FolderEvent:
            def __init__(self, path):
                self.path = path
        app._on_folder_picked(FolderEvent("/tmp/test_output"))
        assert app.output_folder == "/tmp/test_output"
        # Simulate batch file selection for encryption
        class File:
            def __init__(self, path, name):
                self.path = path
                self.name = name
        class FileEvent:
            def __init__(self, files):
                self.files = files
        files = [File(f"/tmp/file{i}.pdf", f"file{i}.pdf") for i in range(3)]
        app.current_page = "encryption"
        app._on_file_picked(FileEvent(files))
        assert len(app.uploaded_files["encryption"]) == 3
        # Simulate drag-and-drop for hashing
        app.current_page = "hashing"
        app._on_file_drop_hash(FileEvent(files))
        assert len(app.uploaded_files["hashing"]) == 3
        print("All batch, drag-and-drop, and output folder picker tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 