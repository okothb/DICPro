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
        self.encryptor = DocumentEncryptor()
        self.hash_generator = HashGenerator()
        self.verifier = DocumentVerifier()
        
    def main(self, page: ft.Page):
        """Main application entry point."""
        self.page = page
        self.page.title = "Document Integrity Protection System"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 20
        self.page.spacing = 20
        # Add favicon to the browser tab
        self.page.favicon = "DocPro.ico"
        self._init_ui_components()
        self.page.app_bar = self.app_bar
        self.page.overlay.append(self.file_picker)
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
        
        # App bar with DocPro.ico
        self.app_bar = ft.AppBar(
            title=ft.Row([
                ft.Image(src="DocPro.ico", width=32, height=32),
                ft.Text("Document Protection System")
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            center_title=True,
            actions=[]
        )
        
        # File picker for all pages
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.folder_file_picker = ft.FilePicker(on_result=self._on_folder_file_picked)
    
    def show_landing_page(self):
        """Display the landing page."""
        self.current_page = "landing"
        
        # Hero section with DocPro.ico
        hero_section = ft.Container(
            content=ft.Column([
                ft.Image(src="DocPro.ico", width=96, height=96),
                ft.Text(
                    "Secure Document Protection",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Advanced encryption, hashing, steganography, and integrity verification for your documents",
                    size=20,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=40),
                ft.Row([
                    ft.ElevatedButton(
                        "Get Started",
                        on_click=self._go_to_dashboard,
                        style=ft.ButtonStyle(
                            padding=20
                        )
                    ),
                    ft.OutlinedButton(
                        "Learn More",
                        on_click=self._show_features
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ]),
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
            ]),
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
    
    def _show_features(self, e):
        """Show detailed features information."""
        features_dialog = ft.AlertDialog(
            title=ft.Text("Document Protection Features"),
            content=ft.Column([
                ft.Text("Advanced Security Features:", weight=ft.FontWeight.BOLD),
                ft.Text("• AES-256 Encryption: Military-grade document protection"),
                ft.Text("• SHA-256 Hashing: Reliable integrity verification"),
                ft.Text("• Digital Signatures: Authentic document validation"),
                ft.Text("• Steganography: Hidden data embedding for covert communication"),
                ft.Text("• Batch Processing: Handle multiple files efficiently"),
                ft.Container(height=10),
                ft.Text("Supported File Types:", weight=ft.FontWeight.BOLD),
                ft.Text("• Documents: PDF, DOCX, TXT"),
                ft.Text("• Images: JPG, PNG"),
                ft.Text("• Spreadsheets: XLSX, CSV"),
                ft.Container(height=10),
                ft.Text("Security & Privacy:", weight=ft.FontWeight.BOLD),
                ft.Text("• Local Processing: No data leaves your device"),
                ft.Text("• No Cloud Storage: Complete privacy control"),
                ft.Text("• Secure Key Management: Industry-standard practices"),
                ft.Text("• Covert Communication: Hidden message embedding")
            ], scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Get Started", on_click=lambda _: self._close_dialog())
            ]
        )
        
        self.page.dialog = features_dialog
        features_dialog.open = True
        self.page.update()
    
    def show_encryption_page(self):
        self.current_page = "encryption"
        password_field = ft.TextField(
            label="Encryption Password",
            password=True,
            hint_text="Enter a strong password",
            width=300
        )
        drag_target = ft.DragTarget(
            group="files",
            content=ft.Container(
                content=ft.Text("Drag and drop files here to encrypt", size=16, text_align=ft.TextAlign.CENTER),
                padding=20,
                border=ft.border.all(2, "#888"),
                border_radius=8,
                bgcolor="#f5f5f5"
            ),
            on_accept=self._on_file_drop_encrypt
        )
        encryption_content = ft.Column([
            ft.Text("Document Encryption", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self._output_folder_section(),
            ft.Container(height=10),
            drag_target,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Choose Files",
                icon="UPLOAD_FILE",
                on_click=lambda _: self.file_picker.pick_files(allow_multiple=True, allowed_extensions=["pdf", "docx", "txt", "jpg", "png"])
            ),
            ft.Container(height=10),
            password_field,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Encrypt Document(s)",
                icon="LOCK",
                on_click=lambda _: self._encrypt_document(password_field.value)
            )
        ])
        self._update_main_layout(encryption_content)

    def _on_file_drop_encrypt(self, e):
        # Accept dropped files for encryption
        if hasattr(e, 'files') and e.files:
            for f in e.files:
                self.uploaded_files.setdefault("encryption", []).append(f.path)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{len(e.files)} file(s) dropped for encryption.")))

    def show_hashing_page(self):
        self.current_page = "hashing"
        drag_target = ft.DragTarget(
            group="files",
            content=ft.Container(
                content=ft.Text("Drag and drop files here to hash", size=16, text_align=ft.TextAlign.CENTER),
                padding=20,
                border=ft.border.all(2, "#888"),
                border_radius=8,
                bgcolor="#f5f5f5"
            ),
            on_accept=self._on_file_drop_hash
        )
        hashing_content = ft.Column([
            ft.Text("Document Hashing", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            drag_target,
            ft.Container(height=10),
            ft.ElevatedButton(
                "Choose Files",
                icon="UPLOAD_FILE",
                on_click=lambda _: self.file_picker.pick_files(allow_multiple=True, allowed_extensions=["pdf", "docx", "txt", "jpg", "png", "xlsx", "csv"])
            ),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Generate Hash(es)",
                icon="FINGERPRINT",
                on_click=self._generate_hash
            )
        ])
        self._update_main_layout(hashing_content)

    def _on_file_drop_hash(self, e):
        if hasattr(e, 'files') and e.files:
            for f in e.files:
                self.uploaded_files.setdefault("hashing", []).append(f.path)
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text(f"{len(e.files)} file(s) dropped for hashing.")))

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
    
    def _handle_route_change(self, route):
        """Handle route changes."""
        pass

    def _nav_change(self, e):
        # Simple navigation handler for NavigationRail
        idx = e.control.selected_index
        if idx == 0:
            self.show_landing_page()
        elif idx == 1:
            self.show_encryption_page()
        elif idx == 2:
            self.show_hashing_page()
        elif idx == 3:
            self.show_verification_page()
        elif idx == 4:
            self.show_steganography_page()
        elif idx == 5:
            self.show_settings_page()

def main():
    """Main entry point for the web application."""
    app = DocumentProtectionWebApp()
    ft.app(target=app.main, view=ft.WEB_BROWSER, port=8550)

if __name__ == "__main__":
    main() 