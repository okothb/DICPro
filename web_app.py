"""
Document Integrity Protection System - Web Application
A Flet-based web interface for document protection and integrity verification.
"""

import flet as ft
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
import base64
import tempfile
import shutil

# Import core modules
from core.encryptor import DocumentEncryptor
from core.hash_generator import HashGenerator
from core.verifier import DocumentVerifier
from core.steganography import DocumentSteganography
from utils.logger import get_logger

# Setup logging
logger = get_logger(__name__)

class DocumentProtectionWebApp:
    """
    Main web application class for Document Integrity Protection System.
    """
    
    def __init__(self):
        """Initialize the web application."""
        self.uploaded_files = {}
        self.current_page = "landing"
        self.output_folder = None
        self.protect_files = []
        self.verify_files = []
        self.encryptor = DocumentEncryptor()
        self.hash_generator = HashGenerator()
        self.verifier = DocumentVerifier()
        self.steganography = DocumentSteganography()
        
    def main(self, page: ft.Page):
        """Main application entry point."""
        self.page = page
        self.page.title = "Document Integrity Protection System"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 20
        self.page.spacing = 20
        self._init_ui_components()
        self.page.app_bar = self.app_bar
        self.page.overlay.append(self.file_picker)
        self.page.overlay.append(self.folder_file_picker)
        self.show_landing_page()
        self.page.on_route_change = self._handle_route_change
        self.page.update()
    
    def _init_ui_components(self):
        """Initialize UI components."""
        # Navigation
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon="HOME_OUTLINED",
                    selected_icon="HOME",
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon="LOCK_OUTLINE",
                    selected_icon="LOCK",
                    label="Encryption"
                ),
                ft.NavigationRailDestination(
                    icon="FINGERPRINT_OUTLINED",
                    selected_icon="FINGERPRINT",
                    label="Hashing"
                ),
                ft.NavigationRailDestination(
                    icon="VERIFIED_OUTLINED",
                    selected_icon="VERIFIED",
                    label="Verification"
                ),
                ft.NavigationRailDestination(
                    icon="HIDDEN_OUTLINED",
                    selected_icon="HIDDEN",
                    label="Steganography"
                ),
                ft.NavigationRailDestination(
                    icon="SETTINGS_OUTLINED",
                    selected_icon="SETTINGS",
                    label="Settings"
                ),
            ],
            on_change=self._nav_change
        )
        
        # Main content area
        self.content_area = ft.Container(
            expand=True,
            content=ft.Text("Welcome to Document Protection System")
        )
        
        # App bar
        self.app_bar = ft.AppBar(
            title=ft.Text("Document Protection System"),
            center_title=True,
            actions=[]
        )
        
        # File picker for all pages
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.folder_file_picker = ft.FilePicker(on_result=self._on_folder_file_picked)
    
    def show_landing_page(self):
        """Display the landing page."""
        self.current_page = "landing"
        
        # Hero section
        hero_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Secure Document Protection",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Advanced protection and verification for your documents",
                    size=20,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=40),
                ft.Row([
                    ft.ElevatedButton(
                        "Get Started",
                        on_click=self._go_to_dashboard,
                        style=ft.ButtonStyle(
                            padding=25,
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            elevation=8
                        )
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=40
        )
        
        # Features section
        features_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Key Features",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                ft.Row([
                    self._create_feature_card(
                        "Encryption",
                        "AES-256 encryption for secure document protection",
                        "LOCK"
                    ),
                    self._create_feature_card(
                        "Hashing",
                        "SHA-256 hashing for document integrity verification",
                        "FINGERPRINT"
                    ),
                    self._create_feature_card(
                        "Verification",
                        "Comprehensive integrity checking and reporting",
                        "VERIFIED"
                    ),
                    self._create_feature_card(
                        "Steganography",
                        "Hidden data embedding for covert communication",
                        "HIDDEN"
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40
        )
        
        # Update page content
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/",
                [hero_section, features_section]
            )
        )
        self.page.update()
    
    def _create_feature_card(self, title: str, description: str, icon) -> ft.Card:
        """Create a feature card for the landing page."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=48),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=14, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=250
            )
        )
    

    
    def _close_dialog(self):
        """Close the current dialog."""
        try:
            if hasattr(self.page, 'dialog') and self.page.dialog:
                self.page.dialog.open = False
                self.page.update()
        except Exception as ex:
            # If dialog closing fails, just update the page
            self.page.update()
    

    
    def _create_protect_tab(self):
        """Create the Protect tab similar to app.py."""
        # State variables are initialized in __init__
        
        # Create file selection section
        file_select = ft.Column([
            ft.Text("📁 Output Folder Selection:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.ElevatedButton("Choose Output Folder", icon="FOLDER", on_click=self._on_choose_output_folder),
            ft.Text("No output folder selected", key="output_folder_text"),
            ft.Container(height=5),
            ft.Text("📄 File Selection:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
            ft.Text("Select files or drag-and-drop here:", size=14, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Choose Files", icon="UPLOAD_FILE", on_click=self._on_choose_files),
            ft.DragTarget(
                content=ft.Container(
                    content=ft.Text("Drag files or folders here", size=12, italic=True),
                    width=300,
                    height=50,
                                    bgcolor=ft.Colors.GREY_200,
                border=ft.border.all(2, ft.Colors.BLUE_200),
                    alignment=ft.alignment.center,
                ),
                on_accept=self._on_protect_drop,
            ),
            ft.ElevatedButton("Choose Folder (Batch)", icon="FOLDER", on_click=self._on_choose_folder),
            ft.Container(height=5),
        ], spacing=8)
        
        # Add encryption controls
        encrypt_checkbox = ft.Checkbox(label="Enable Encryption", value=False)
        password_field = ft.TextField(label="Encryption Password", password=True, visible=False)
        
        def on_encrypt_toggle(e):
            password_field.visible = encrypt_checkbox.value
            self.page.update()
        
        encrypt_checkbox.on_change = on_encrypt_toggle
        file_select.controls.append(encrypt_checkbox)
        file_select.controls.append(password_field)
        
        # Secret data input
        secret_data_field = ft.TextField(label="Secret Data to Embed", multiline=True, min_lines=1, max_lines=2)
        secret_file_btn = ft.ElevatedButton("Choose Secret Data File", icon="ATTACH_FILE", on_click=self._on_choose_secret_file)
        file_select.controls.append(secret_data_field)
        file_select.controls.append(secret_file_btn)
        
        # Process button
        process_btn = ft.ElevatedButton("Process", icon="PLAY_ARROW", on_click=self._process_files)
        file_select.controls.append(process_btn)
        
        # Progress section
        progress_section = ft.Column([
            ft.Text("Progress:", size=13, weight=ft.FontWeight.BOLD),
            ft.ProgressBar(width=300, value=0, color="blue"),
            ft.Text("No processing yet.", key="progress_text", size=12),
        ], spacing=5)
        
        # Output section
        output_list = ft.ListView(spacing=5, padding=5, expand=True)
        output_section = ft.Column([
            ft.Text("Output:", size=13, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=output_list,
                height=150,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=5,
            ),
        ], spacing=5)
        
        # Store references for later use
        self.protect_file_select = file_select
        self.protect_progress_section = progress_section
        self.protect_output_list = output_list
        self.protect_password_field = password_field
        self.protect_secret_data_field = secret_data_field
        
        return ft.Column([
            file_select,
            progress_section,
            output_section,
        ], expand=True, spacing=15)
    
    def _create_verify_tab(self):
        """Create the Verify tab similar to app.py."""
        # State variables are initialized in __init__
        
        # Verification controls
        verify_btn = ft.ElevatedButton("Choose Files", icon="UPLOAD_FILE", on_click=self._on_verify_choose_files)
        verify_process_btn = ft.ElevatedButton("Verify Documents", icon="VERIFIED", on_click=self._verify_documents)
        
        # Drag target for verification
        verify_drag_target = ft.DragTarget(
            content=ft.Container(
                content=ft.Text("Drag files here for verification", size=12, italic=True),
                width=300,
                height=50,
                            bgcolor=ft.Colors.GREY_200,
            border=ft.border.all(2, ft.Colors.GREEN_200),
                alignment=ft.alignment.center,
            ),
            on_accept=self._on_verify_drop,
        )
        
        # Progress section
        verify_progress = ft.ProgressBar(width=300, value=0, color="green")
        verify_status = ft.Text("No verification yet.")
        verify_progress_section = ft.Column([
            ft.Text("Progress:", size=16, weight=ft.FontWeight.BOLD),
            verify_progress,
            verify_status,
        ], spacing=10)
        
        # Output section
        verify_output_list = ft.ListView(spacing=5, padding=5, expand=True)
        verify_output_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    verify_output_list,
                ], expand=True),
                padding=10,
                bgcolor=ft.Colors.WHITE,
            ),
            elevation=3,
        )
        
        # Extraction functionality
        extract_btn = ft.ElevatedButton("Extract Payload(s)", icon="DOWNLOAD", on_click=self._extract_payloads)
        extract_output_list = ft.ListView(expand=1, spacing=10, padding=10)
        
        # Store references for later use
        self.verify_progress = verify_progress
        self.verify_status = verify_status
        self.verify_output_list = verify_output_list
        self.extract_output_list = extract_output_list
        
        return ft.Column([
            ft.Text("Document Verification", size=18, weight=ft.FontWeight.BOLD),
            ft.Row([
                verify_btn,
                verify_process_btn,
            ], spacing=10),
            verify_drag_target,
            verify_progress_section,
            verify_output_card,
            extract_btn,
            extract_output_list,
        ], expand=True, spacing=20)
    
    def _update_main_layout(self, content):
        """Update the main layout with new content."""
        self.content_area.content = content
        # Ensure we're in the main app layout
        if len(self.page.views) == 1 and self.page.views[0].route == "/":
            self._go_to_dashboard(None)
        else:
            self.page.update()
    
    # Event handlers for Protect tab
    def _on_choose_output_folder(self, e):
        """Choose output folder for protected files."""
        def folder_chosen(result):
            if result.path:
                self.output_folder = result.path
                # Update the output folder text
                for control in self.protect_file_select.controls:
                    if hasattr(control, 'key') and control.key == "output_folder_text":
                        control.value = f"Selected: {result.path}"
                        break
                self.page.update()
        self.folder_file_picker.on_result = folder_chosen
        self.folder_file_picker.get_directory_path()
    
    def _on_choose_files(self, e):
        """Choose files for protection."""
        def files_chosen(result):
            if result.files:
                added = 0
                for f in result.files:
                    # Basic file safety check
                    if os.path.exists(f.path) and os.path.isfile(f.path):
                        self.protect_files.append(f.path)
                        self.protect_output_list.controls.append(ft.Text(f"Selected: {f.path}"))
                        added += 1
                if added:
                    self.protect_output_list.update()
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{added} file(s) selected and accepted.")))
                    self.page.update()
        self.file_picker.on_result = files_chosen
        self.file_picker.pick_files(allow_multiple=True)
    
    def _on_protect_drop(self, e):
        """Handle file drop for protection."""
        if hasattr(e, 'files') and e.files:
            added = 0
            for f in e.files:
                if os.path.exists(f.path) and os.path.isfile(f.path):
                    self.protect_files.append(f.path)
                    self.protect_output_list.controls.append(ft.Text(f"Selected: {f.path}"))
                    added += 1
            if added:
                self.protect_output_list.update()
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{added} file(s) dropped and accepted.")))
                self.page.update()
    
    def _on_choose_folder(self, e):
        """Choose folder for batch processing."""
        def folder_chosen(result):
            if result.path:
                folder_path = result.path
                files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                added = 0
                for f in files:
                    if os.path.exists(f) and os.path.isfile(f):
                        self.protect_files.append(f)
                        self.protect_output_list.controls.append(ft.Text(f"Selected: {f}"))
                        added += 1
                if added:
                    self.protect_output_list.update()
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{added} file(s) from folder selected.")))
                    self.page.update()
        self.folder_file_picker.on_result = folder_chosen
        self.folder_file_picker.get_directory_path()
    
    def _on_choose_secret_file(self, e):
        """Choose secret data file."""
        def file_chosen(result):
            if result.files:
                secret_file_path = result.files[0].path
                try:
                    with open(secret_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        self.protect_secret_data_field.value = f.read()
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Loaded secret data from {secret_file_path}")))
                    self.page.update()
                except Exception as ex:
                    self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Error loading file: {str(ex)}")))
                    self.page.update()
        self.file_picker.on_result = file_chosen
        self.file_picker.pick_files(allow_multiple=False)
    
    def _process_files(self, e):
        """Process files for protection (encryption, hashing, steganography)."""
        if not self.protect_files:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("No files selected for processing.")))
            self.page.update()
            return
        
        if not self.output_folder:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please select an output folder first.")))
            self.page.update()
            return
        
        # Clear output list
        self.protect_output_list.controls.clear()
        
        # Get secret data
        user_secret = self.protect_secret_data_field.value or "Default secret data"
        
        # Process each file
        total = len(self.protect_files)
        for idx, file_path in enumerate(self.protect_files):
            try:
                filename = os.path.basename(file_path)
                output_file = os.path.join(self.output_folder, f"protected_{filename}")
                
                # Generate original hash
                original_hash = self.hash_generator.generate_file_hash(file_path)
                
                # Process based on file type
                ext = os.path.splitext(file_path)[1].lower()
                result = None
                
                if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    # Image steganography
                    result = self.steganography.hide_data_in_image(file_path, user_secret, output_file)
                    if result and result.get('success'):
                        protected_hash = self.hash_generator.generate_file_hash(output_file)
                        self.hash_generator.save_hash_to_file(file_path, original_hash, hash_type="original")
                        self.hash_generator.save_hash_to_file(output_file, protected_hash, hash_type="protected")
                elif ext == ".pdf":
                    # PDF steganography
                    result = self.steganography.hide_data_in_pdf(file_path, user_secret, output_file)
                    if result and result.get('success'):
                        protected_hash = self.hash_generator.generate_file_hash(output_file)
                        self.hash_generator.save_hash_to_file(file_path, original_hash, hash_type="original")
                        self.hash_generator.save_hash_to_file(output_file, protected_hash, hash_type="protected")
                elif ext in [".xlsx", ".xls", ".csv"]:
                    # Excel steganography
                    result = self.steganography.hide_data_in_excel(file_path, user_secret, output_file)
                    if result and result.get('success'):
                        protected_hash = self.hash_generator.generate_file_hash(output_file)
                        self.hash_generator.save_hash_to_file(file_path, original_hash, hash_type="original")
                        self.hash_generator.save_hash_to_file(output_file, protected_hash, hash_type="protected")
                else:
                    # Default to encryption
                    if self.protect_password_field.visible and self.protect_password_field.value:
                        result = self.encryptor.encrypt_file(file_path, output_file, self.protect_password_field.value)
                    else:
                        result = {'success': True, 'method': 'hash_only'}
                
                if result and result.get('success'):
                    msg = f"Protected: {file_path} -> {output_file}\nMethod: {result.get('method', 'unknown')}"
                    color = "green"
                else:
                    error_msg = result.get('error', 'Unknown error') if result else 'Unknown error'
                    msg = f"Failed: {file_path}\nError: {error_msg}"
                    color = "red"
                
                self.protect_output_list.controls.append(ft.Text(msg, color=color))
                
                # Update progress
                progress = int(((idx + 1) / total) * 100)
                self.protect_progress_section.controls[1].value = progress / 100
                self.protect_progress_section.controls[2].value = f"{progress}% complete"
                self.protect_output_list.update()
                self.page.update()
                
            except Exception as ex:
                msg = f"Failed: {file_path}\nError: {str(ex)}"
                self.protect_output_list.controls.append(ft.Text(msg, color="red"))
                self.protect_output_list.update()
                self.page.update()
        
        self.protect_progress_section.controls[2].value = "Processing complete."
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Processing complete.")))
        self.page.update()
    
    # Event handlers for Verify tab
    def _on_verify_choose_files(self, e):
        """Choose files for verification."""
        def files_chosen(result):
            if result.files:
                for f in result.files:
                    self.verify_files.append(f.path)
                    self.verify_output_list.controls.append(ft.Text(f"Selected: {f.path}"))
                self.verify_output_list.update()
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{len(result.files)} file(s) selected for verification.")))
                self.page.update()
        self.file_picker.on_result = files_chosen
        self.file_picker.pick_files(allow_multiple=True)
    
    def _on_verify_drop(self, e):
        """Handle file drop for verification."""
        if hasattr(e, 'files') and e.files:
            for f in e.files:
                self.verify_files.append(f.path)
                self.verify_output_list.controls.append(ft.Text(f"Selected: {f.path}"))
            self.verify_output_list.update()
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{len(e.files)} file(s) added for verification.")))
            self.page.update()
    
    def _verify_documents(self, e):
        """Verify documents for integrity and extract data."""
        if not self.verify_files:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("No files selected for verification.")))
            self.page.update()
            return
        
        self.verify_output_list.controls.clear()
        total = len(self.verify_files)
        
        for idx, file_path in enumerate(self.verify_files):
            try:
                ext = os.path.splitext(file_path)[1].lower()
                result = None
                msg = ""
                color = "red"
                
                if ext in [".xlsx", ".xls", ".csv"]:
                    result = self.steganography.extract_data_from_excel(file_path)
                    if result.get('success'):
                        msg = f"Extracted from: {file_path}\nMethod: {result.get('method', 'unknown')}\nMetadata: {result.get('metadata', {})}"
                        color = "green"
                    else:
                        msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
                elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    result = self.steganography.extract_data_from_image(file_path)
                    if result.get('success'):
                        current_hash = self.hash_generator.generate_file_hash(file_path)
                        stored_hash = self.hash_generator.load_hash_from_file(file_path, hash_type="protected")
                        match = (current_hash == stored_hash)
                        msg = f"Verified: {file_path}\nStatus: {'VERIFIED' if match else 'NOT VERIFIED'}\nCurrent Hash: {current_hash}\nStored Hash: {stored_hash}"
                        color = "green" if match else "orange"
                    else:
                        msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
                elif ext == ".pdf":
                    result = self.steganography.extract_data_from_pdf(file_path)
                    if result.get('success'):
                        current_hash = self.hash_generator.generate_file_hash(file_path)
                        stored_hash = self.hash_generator.load_hash_from_file(file_path, hash_type="protected")
                        match = (current_hash == stored_hash)
                        msg = f"Verified: {file_path}\nStatus: {'VERIFIED' if match else 'NOT VERIFIED'}\nCurrent Hash: {current_hash}\nStored Hash: {stored_hash}"
                        color = "green" if match else "orange"
                    else:
                        msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
                else:
                    msg = f"Verification not supported for: {file_path}"
                
                self.verify_output_list.controls.append(ft.Text(msg, color=color))
                
                # Update progress
                progress = int(((idx + 1) / total) * 100)
                self.verify_progress.value = progress / 100
                self.verify_status.value = f"{progress}% complete"
                self.verify_output_list.update()
                self.page.update()
                
            except Exception as ex:
                msg = f"Failed: {file_path}\nError: {str(ex)}"
                self.verify_output_list.controls.append(ft.Text(msg, color="red"))
                self.verify_output_list.update()
                self.page.update()
        
        self.verify_status.value = "Verification complete."
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Verification complete.")))
        self.page.update()
    
    def _extract_payloads(self, e):
        """Extract payloads from verified files."""
        if not self.verify_files:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("No files selected for extraction.")))
            self.page.update()
            return
        
        self.extract_output_list.controls.clear()
        total = len(self.verify_files)
        
        for idx, file_path in enumerate(self.verify_files):
            try:
                ext = os.path.splitext(file_path)[1].lower()
                result = None
                
                if ext in [".xlsx", ".xls", ".csv"]:
                    result = self.steganography.extract_data_from_excel(file_path)
                elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                    result = self.steganography.extract_data_from_image(file_path)
                elif ext == ".pdf":
                    result = self.steganography.extract_data_from_pdf(file_path)
                
                if result and result.get('success'):
                    payload = result.get('secret_data', b'').decode(errors='ignore')
                    hashes = f"Original Hash: {result.get('original_hash')}\nProtected Hash: {result.get('protected_hash')}"
                    match = (result.get('original_hash') == result.get('protected_hash'))
                    msg = f"Extracted from: {file_path}\nPayload: {payload}\n{hashes}\nHashes Match: {'YES' if match else 'NO'}"
                    color = "green" if match else "orange"
                else:
                    msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error') if result else 'Unknown error'}"
                    color = "red"
                
                self.extract_output_list.controls.append(ft.Text(msg, color=color))
                self.extract_output_list.update()
                self.page.update()
                
            except Exception as ex:
                msg = f"Failed: {file_path}\nError: {str(ex)}"
                self.extract_output_list.controls.append(ft.Text(msg, color="red"))
                self.extract_output_list.update()
                self.page.update()
        
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Extraction complete.")))
        self.page.update()
    




    def show_verification_page(self):
        self.current_page = "verification"
        drag_target = ft.DragTarget(
            group="files",
            content=ft.Container(
                content=ft.Text("Drag and drop files here to verify", size=16, text_align=ft.TextAlign.CENTER),
                padding=20,
                border=ft.border.all(2, "#888"),
                border_radius=8,
                bgcolor="#f5f5f5"
            ),
            on_accept=self._on_file_drop_verify
        )
        verification_content = ft.Column([
            ft.Text("Document Verification", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            drag_target,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Choose Files",
                icon="UPLOAD_FILE",
                on_click=lambda _: self.file_picker.pick_files(allow_multiple=True, allowed_extensions=["pdf", "docx", "txt", "jpg", "png"])
            ),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Verify Document(s)",
                icon="VERIFIED",
                on_click=self._verify_document
            )
        ])
        self._update_main_layout(verification_content)

    def _on_file_drop_verify(self, e):
        if hasattr(e, 'files') and e.files:
            for f in e.files:
                self.uploaded_files.setdefault("verification", []).append(f.path)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{len(e.files)} file(s) dropped for verification.")))

    def show_steganography_page(self):
        self.current_page = "steganography"
        drag_target = ft.DragTarget(
            group="files",
            content=ft.Container(
                content=ft.Text("Drag and drop files here for steganography", size=16, text_align=ft.TextAlign.CENTER),
                padding=20,
                border=ft.border.all(2, "#888"),
                border_radius=8,
                bgcolor="#f5f5f5"
            ),
            on_accept=self._on_file_drop_steg
        )
        steganography_content = ft.Column([
            ft.Text("Document Steganography", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self._output_folder_section(),
            ft.Container(height=10),
            drag_target,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Choose Files",
                icon="UPLOAD_FILE",
                on_click=lambda _: self.file_picker.pick_files(allow_multiple=True, allowed_extensions=["jpg", "png", "pdf", "docx"])
            ),
            ft.Container(height=10),
            ft.TextField(
                label="Secret Message",
                hint_text="Enter the message to hide",
                width=300,
                multiline=True,
                min_lines=3,
                max_lines=5
            ),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Hide Message(s)",
                icon="HIDDEN",
                on_click=self._hide_message
            ),
            ft.Container(height=30),
            ft.ElevatedButton(
                "Extract Hidden Message(s)",
                icon="SEARCH",
                on_click=self._extract_message
            )
        ])
        self._update_main_layout(steganography_content)

    def _on_file_drop_steg(self, e):
        if hasattr(e, 'files') and e.files:
            for f in e.files:
                self.uploaded_files.setdefault("steganography", []).append(f.path)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{len(e.files)} file(s) dropped for steganography.")))

    def show_settings_page(self):
        """Display the settings page."""
        self.current_page = "settings"
        settings_content = ft.Column([
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Application Information", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Text("DocPro Web Application"),
                        ft.Text("Version: 1.0.0"),
                        ft.Text("All features are available. No authentication required."),
                        ft.Container(height=10),
                        ft.Text("For support, contact the developer."),
                    ]),
                    padding=20
                )
            )
        ])
        self._update_main_layout(settings_content)
    
    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file selection for all pages."""
        if e.files:
            for f in e.files:
                file_path = f.path
                file_name = f.name
                
                # Store file based on current page
                if self.current_page == "encryption":
                    self.uploaded_files.setdefault("encryption", []).append(file_path)
                elif self.current_page == "hashing":
                    self.uploaded_files.setdefault("hashing", []).append(file_path)
                elif self.current_page == "verification":
                    self.uploaded_files.setdefault("verification", []).append(file_path)
                elif self.current_page == "steganography":
                    self.uploaded_files.setdefault("steganography", []).append(file_path)
                
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"File selected: {file_name}"))
                )
    
    def _on_folder_file_picked(self, e):
        if e.files and len(e.files) > 0:
            folder_path = os.path.dirname(e.files[0].path)
            self.output_folder = folder_path
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Output folder set: {self.output_folder}")))
            self.page.update()

    def _output_folder_section(self):
        return ft.Row([
            ft.Text(f"Output Folder: {self.output_folder if self.output_folder else 'Not selected'}", size=14),
            ft.ElevatedButton(
                "Browse",
                icon="FOLDER",
                on_click=lambda _: self.folder_file_picker.pick_files(allow_multiple=False)
            ),
            ft.TextField(
                value=self.output_folder or "",
                label="Or enter folder path",
                width=300,
                on_change=self._on_output_folder_text
            )
        ], alignment=ft.MainAxisAlignment.START)

    def _on_output_folder_text(self, e):
        self.output_folder = e.control.value
        self.page.update()

    def _encrypt_document(self, password: str):
        """Encrypt the uploaded document."""
        if "encryption" not in self.uploaded_files or not self.uploaded_files["encryption"]:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a file first"))
            )
            return
        
        if not password:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please enter a password"))
            )
            return
        
        try:
            file_paths = self.uploaded_files["encryption"]
            output_paths = [f.replace(".", "_encrypted.") for f in file_paths]
            
            # Use the core encryptor
            results = []
            for i, file_path in enumerate(file_paths):
                result = self.encryptor.encrypt_file(
                    input_file=file_path,
                    output_file=output_paths[i],
                    password=password
                )
                results.append(result)
            
            success_count = sum(1 for r in results if r.get("success"))
            failed_count = sum(1 for r in results if not r.get("success"))
            
            if success_count > 0:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Successfully encrypted {success_count} file(s)."),
                        action="OK"
                    )
                )
            if failed_count > 0:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Failed to encrypt {failed_count} file(s)."),
                        action="OK"
                    )
                )
                
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Encryption error: {str(e)}"),
                    action="OK"
                )
            )
    
    def _generate_hash(self, e):
        """Generate hash for the uploaded document."""
        if "hashing" not in self.uploaded_files or not self.uploaded_files["hashing"]:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a file first"))
            )
            return
        
        try:
            file_paths = self.uploaded_files["hashing"]
            
            # Use the core hash generator
            for file_path in file_paths:
                hash_value = self.hash_generator.generate_file_hash(file_path)
                
                if hash_value:
                    # Save hash
                    self.hash_generator.save_hash_to_file(file_path, hash_value, "original")
                    
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"Hash generated: {hash_value[:16]}... for {os.path.basename(file_path)}"),
                            action="OK"
                        )
                    )
                else:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"Failed to generate hash for {os.path.basename(file_path)}"),
                            action="OK"
                        )
                    )
                
        except Exception as e:
            logger.error(f"Hash generation error: {str(e)}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Hash generation error: {str(e)}"),
                    action="OK"
                )
            )
    
    def _verify_document(self, e):
        """Verify the uploaded document."""
        if "verification" not in self.uploaded_files or not self.uploaded_files["verification"]:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a file first"))
            )
            return
        
        try:
            file_paths = self.uploaded_files["verification"]
            
            # Use the core verifier
            results = []
            for file_path in file_paths:
                result = self.verifier.verify_protected_document(file_path)
                results.append(result)
            
            success_count = sum(1 for r in results if r.get("integrity_verified"))
            failed_count = sum(1 for r in results if not r.get("integrity_verified"))
            
            if success_count > 0:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Successfully verified {success_count} file(s)."),
                        action="OK"
                    )
                )
            if failed_count > 0:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Failed to verify {failed_count} file(s)."),
                        action="OK"
                    )
                )
                
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Verification error: {str(e)}"),
                    action="OK"
                )
            )
    
    def _hide_message(self, e):
        """Hide message in document using steganography."""
        if "steganography" not in self.uploaded_files or not self.uploaded_files["steganography"]:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a carrier file first"))
            )
            return
        
        try:
            file_paths = self.uploaded_files["steganography"]
            
            # For demo purposes, simulate steganography
            # In a real implementation, you'd use the core steganography module
            for file_path in file_paths:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Message hidden successfully! (Demo mode) for {os.path.basename(file_path)}"),
                        action="OK"
                    )
                )
                
        except Exception as e:
            logger.error(f"Steganography error: {str(e)}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Steganography error: {str(e)}"),
                    action="OK"
                )
            )
    
    def _extract_message(self, e):
        """Extract hidden message from document."""
        if "steganography" not in self.uploaded_files or not self.uploaded_files["steganography"]:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a file to analyze first"))
            )
            return
        
        try:
            file_paths = self.uploaded_files["steganography"]
            
            # For demo purposes, simulate message extraction
            # In a real implementation, you'd use the core steganography module
            for file_path in file_paths:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Hidden message extracted! (Demo mode) for {os.path.basename(file_path)}"),
                        action="OK"
                    )
                )
                
        except Exception as e:
            logger.error(f"Message extraction error: {str(e)}")
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Message extraction error: {str(e)}"),
                    action="OK"
                )
            )
    
    def _go_to_encryption(self, e):
        """Navigate to encryption page."""
        self.nav_rail.selected_index = 1
        self.show_encryption_page()
    
    def _go_to_hashing(self, e):
        """Navigate to hashing page."""
        self.nav_rail.selected_index = 2
        self.show_hashing_page()
    
    def _go_to_verification(self, e):
        """Navigate to verification page."""
        self.nav_rail.selected_index = 3
        self.show_verification_page()
    
    def _go_to_dashboard(self, e):
        """Navigate to main application interface with app.py structure."""
        # Create the main application layout with tabs like app.py
        self.page.views.clear()
        
        # Create the tabs structure similar to app.py
        tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Protect", content=self._create_protect_tab()),
                ft.Tab(text="Verify", content=self._create_verify_tab()),
            ],
            expand=True,
        )
        
        self.page.views.append(
            ft.View(
                "/app",
                [tabs]
            )
        )
        self.page.update()
    
    def _handle_route_change(self, route):
        """Handle route changes."""
        pass

    def _nav_change(self, e):
        # Navigation handler - simplified since we're using tabs now
        idx = e.control.selected_index
        if idx == 0:
            # Show landing page
            self.show_landing_page()
        else:
            # Any other navigation goes to the main app
            if len(self.page.views) == 1 and self.page.views[0].route == "/":
                self._go_to_dashboard(None)

def main():
    """Main entry point for the web application."""
    app = DocumentProtectionWebApp()
    ft.app(target=app.main)

if __name__ == "__main__":
    main() 