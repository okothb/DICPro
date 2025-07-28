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
        self.current_user = None
        self.user_subscription = None
        self.encryptor = DocumentEncryptor()
        self.hash_generator = HashGenerator()
        self.verifier = DocumentVerifier()
        
        # Authentication state
        self.is_authenticated = False
        self.auth_provider = None
        
        # UI state
        self.current_page = "landing"
        self.uploaded_files = {}
        
    def main(self, page: ft.Page):
        """Main application entry point."""
        self.page = page
        self.page.title = "Document Integrity Protection System"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.padding = 20
        self.page.spacing = 20
        
        # Initialize UI components
        self._init_ui_components()
        
        # Show landing page initially
        self.show_landing_page()
        
        # Handle page updates
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
                    icon=ft.icons.HOME_OUTLINED,
                    selected_icon=ft.icons.HOME,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.LOCK_OUTLINE,
                    selected_icon=ft.icons.LOCK,
                    label="Encryption"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.FINGERPRINT_OUTLINED,
                    selected_icon=ft.icons.FINGERPRINT,
                    label="Hashing"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.VERIFIED_OUTLINED,
                    selected_icon=ft.icons.VERIFIED,
                    label="Verification"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS_OUTLINED,
                    selected_icon=ft.icons.SETTINGS,
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
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    on_click=self._logout,
                    visible=False
                )
            ]
        )
    
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
                    text_align=ft.TextAlign.CENTER,
                    color=ft.colors.PRIMARY
                ),
                ft.Text(
                    "Advanced encryption, hashing, and integrity verification for your documents",
                    size=20,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.colors.ON_SURFACE_VARIANT
                ),
                ft.Container(height=40),
                ft.Row([
                    ft.ElevatedButton(
                        "Get Started",
                        on_click=self._show_auth_options,
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.PRIMARY,
                            color=ft.colors.ON_PRIMARY,
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
                        ft.icons.LOCK
                    ),
                    self._create_feature_card(
                        "Hashing",
                        "SHA-256 hashing for document integrity verification",
                        ft.icons.FINGERPRINT
                    ),
                    self._create_feature_card(
                        "Verification",
                        "Comprehensive integrity checking and reporting",
                        ft.icons.VERIFIED
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
                [hero_section, features_section],
                app_bar=self.app_bar
            )
        )
        self.page.update()
    
    def _create_feature_card(self, title: str, description: str, icon) -> ft.Card:
        """Create a feature card for the landing page."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=48, color=ft.colors.PRIMARY),
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
                ft.Text("• Secure Key Management: Industry-standard practices")
            ], scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Get Started", on_click=lambda _: self._close_dialog())
            ]
        )
        
        self.page.dialog = features_dialog
        features_dialog.open = True
        self.page.update()
    
    def _show_auth_options(self, e):
        """Show authentication options."""
        auth_dialog = ft.AlertDialog(
            title=ft.Text("Sign In"),
            content=ft.Column([
                ft.Text("Choose your preferred sign-in method:"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Continue with Google",
                    icon=ft.icons.GOOGLE,
                    on_click=lambda _: self._authenticate("google"),
                    style=ft.ButtonStyle(bgcolor=ft.colors.RED_400)
                ),
                ft.ElevatedButton(
                    "Continue with GitHub",
                    icon=ft.icons.CODE,
                    on_click=lambda _: self._authenticate("github"),
                    style=ft.ButtonStyle(bgcolor=ft.colors.GREY_800)
                ),
                ft.ElevatedButton(
                    "Continue with Apple",
                    icon=ft.icons.APPLE,
                    on_click=lambda _: self._authenticate("apple"),
                    style=ft.ButtonStyle(bgcolor=ft.colors.BLACK)
                )
            ], spacing=10)
        )
        
        self.page.dialog = auth_dialog
        auth_dialog.open = True
        self.page.update()
    
    def _authenticate(self, provider: str):
        """Handle authentication with social providers."""
        # For demo purposes, we'll simulate authentication
        # In a real implementation, you'd integrate with OAuth providers
        
        self.auth_provider = provider
        self.current_user = {
            "id": "demo_user_123",
            "name": f"Demo User ({provider.title()})",
            "email": f"demo@{provider}.com",
            "provider": provider
        }
        
        # Check subscription status (placeholder for paywall)
        self.user_subscription = {
            "status": "free",
            "features": ["encryption", "hashing"],
            "limits": {"files_per_day": 5}
        }
        
        self.is_authenticated = True
        self.page.dialog.open = False
        self.page.update()
        
        # Show main dashboard
        self.show_dashboard()
        
        # Show welcome message
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"Welcome, {self.current_user['name']}!"),
                action="OK"
            )
        )
    
    def show_dashboard(self):
        """Display the main dashboard."""
        self.current_page = "dashboard"
        
        # Update app bar
        self.app_bar.actions[0].visible = True
        
        # Dashboard content
        dashboard_content = ft.Column([
            ft.Text(
                f"Welcome back, {self.current_user['name']}!",
                size=24,
                weight=ft.FontWeight.BOLD
            ),
            ft.Container(height=20),
            
            # Quick stats
            ft.Row([
                self._create_stat_card("Files Protected", "0", ft.icons.SHIELD),
                self._create_stat_card("Hashes Generated", "0", ft.icons.FINGERPRINT),
                self._create_stat_card("Verifications", "0", ft.icons.VERIFIED)
            ]),
            
            ft.Container(height=30),
            
            # Quick actions
            ft.Text("Quick Actions", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Row([
                ft.ElevatedButton(
                    "Encrypt Document",
                    icon=ft.icons.LOCK,
                    on_click=lambda _: self._nav_change(ft.ControlEvent(1))
                ),
                ft.ElevatedButton(
                    "Generate Hash",
                    icon=ft.icons.FINGERPRINT,
                    on_click=lambda _: self._nav_change(ft.ControlEvent(2))
                ),
                ft.ElevatedButton(
                    "Verify Document",
                    icon=ft.icons.VERIFIED,
                    on_click=lambda _: self._nav_change(ft.ControlEvent(3))
                )
            ], spacing=10)
        ])
        
        # Update layout
        self._update_main_layout(dashboard_content)
    
    def _create_stat_card(self, title: str, value: str, icon) -> ft.Card:
        """Create a statistics card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=32, color=ft.colors.PRIMARY),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(title, size=14)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                width=150
            )
        )
    
    def _update_main_layout(self, content):
        """Update the main layout with navigation and content."""
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/dashboard",
                [
                    ft.Row([
                        self.nav_rail,
                        ft.VerticalDivider(width=1),
                        ft.Column([
                            content
                        ], expand=True)
                    ], expand=True)
                ],
                app_bar=self.app_bar
            )
        )
        self.page.update()
    
    def _nav_change(self, e):
        """Handle navigation changes."""
        if not self.is_authenticated:
            self.show_landing_page()
            return
        
        page_index = e.control.selected_index
        if page_index == 0:
            self.show_dashboard()
        elif page_index == 1:
            self.show_encryption_page()
        elif page_index == 2:
            self.show_hashing_page()
        elif page_index == 3:
            self.show_verification_page()
        elif page_index == 4:
            self.show_settings_page()
    
    def show_encryption_page(self):
        """Display the encryption page."""
        self.current_page = "encryption"
        
        # File picker
        file_picker = ft.FilePicker(on_result=self._on_encryption_file_picked)
        self.page.overlay.append(file_picker)
        
        # Password input
        password_field = ft.TextField(
            label="Encryption Password",
            password=True,
            hint_text="Enter a strong password",
            width=300
        )
        
        # Encryption content
        encryption_content = ft.Column([
            ft.Text("Document Encryption", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Upload Document", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Choose File",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: file_picker.pick_files(
                                allowed_extensions=["pdf", "docx", "txt", "jpg", "png"]
                            )
                        ),
                        ft.Container(height=10),
                        password_field,
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Encrypt Document",
                            icon=ft.icons.LOCK,
                            on_click=lambda _: self._encrypt_document(password_field.value)
                        )
                    ]),
                    padding=20
                )
            )
        ])
        
        self._update_main_layout(encryption_content)
    
    def show_hashing_page(self):
        """Display the hashing page."""
        self.current_page = "hashing"
        
        # File picker
        file_picker = ft.FilePicker(on_result=self._on_hashing_file_picked)
        self.page.overlay.append(file_picker)
        
        # Hashing content
        hashing_content = ft.Column([
            ft.Text("Document Hashing", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Generate Hash", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Choose File",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: file_picker.pick_files(
                                allowed_extensions=["pdf", "docx", "txt", "jpg", "png", "xlsx", "csv"]
                            )
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Generate Hash",
                            icon=ft.icons.FINGERPRINT,
                            on_click=self._generate_hash
                        )
                    ]),
                    padding=20
                )
            )
        ])
        
        self._update_main_layout(hashing_content)
    
    def show_verification_page(self):
        """Display the verification page."""
        self.current_page = "verification"
        
        # File picker
        file_picker = ft.FilePicker(on_result=self._on_verification_file_picked)
        self.page.overlay.append(file_picker)
        
        # Verification content
        verification_content = ft.Column([
            ft.Text("Document Verification", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Verify Document", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Choose File",
                            icon=ft.icons.UPLOAD_FILE,
                            on_click=lambda _: file_picker.pick_files(
                                allowed_extensions=["pdf", "docx", "txt", "jpg", "png"]
                            )
                        ),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Verify Integrity",
                            icon=ft.icons.VERIFIED,
                            on_click=self._verify_document
                        )
                    ]),
                    padding=20
                )
            )
        ])
        
        self._update_main_layout(verification_content)
    
    def show_settings_page(self):
        """Display the settings page."""
        self.current_page = "settings"
        
        # Subscription info
        subscription_status = "Free" if self.user_subscription["status"] == "free" else "Premium"
        
        settings_content = ft.Column([
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Account Information", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.Text(f"Name: {self.current_user['name']}"),
                        ft.Text(f"Email: {self.current_user['email']}"),
                        ft.Text(f"Provider: {self.current_user['provider'].title()}"),
                        ft.Container(height=10),
                        ft.Text(f"Subscription: {subscription_status}"),
                        ft.Container(height=20),
                        
                        # Paywall placeholder
                        ft.Text("Upgrade to Premium", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text("Get unlimited access to all features"),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Upgrade Now",
                            icon=ft.icons.STAR,
                            on_click=self._show_paywall
                        )
                    ]),
                    padding=20
                )
            )
        ])
        
        self._update_main_layout(settings_content)
    
    def _show_paywall(self, e):
        """Show paywall dialog (placeholder)."""
        paywall_dialog = ft.AlertDialog(
            title=ft.Text("Upgrade to Premium"),
            content=ft.Column([
                ft.Text("Premium Features:"),
                ft.Text("• Unlimited file processing"),
                ft.Text("• Advanced encryption options"),
                ft.Text("• Priority support"),
                ft.Text("• Detailed analytics"),
                ft.Container(height=20),
                ft.Text("Coming soon! This is a placeholder for future paywall integration.")
            ]),
            actions=[
                ft.TextButton("Close", on_click=lambda _: self._close_dialog())
            ]
        )
        
        self.page.dialog = paywall_dialog
        paywall_dialog.open = True
        self.page.update()
    
    def _close_dialog(self):
        """Close the current dialog."""
        self.page.dialog.open = False
        self.page.update()
    
    def _logout(self, e):
        """Handle user logout."""
        self.is_authenticated = False
        self.current_user = None
        self.user_subscription = None
        self.auth_provider = None
        
        # Clear uploaded files
        self.uploaded_files.clear()
        
        # Show landing page
        self.show_landing_page()
        
        # Update app bar
        self.app_bar.actions[0].visible = False
        self.page.update()
    
    def _on_encryption_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file selection for encryption."""
        if e.files:
            file_path = e.files[0].path
            self.uploaded_files["encryption"] = file_path
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"File selected: {e.files[0].name}"))
            )
    
    def _on_hashing_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file selection for hashing."""
        if e.files:
            file_path = e.files[0].path
            self.uploaded_files["hashing"] = file_path
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"File selected: {e.files[0].name}"))
            )
    
    def _on_verification_file_picked(self, e: ft.FilePickerResultEvent):
        """Handle file selection for verification."""
        if e.files:
            file_path = e.files[0].path
            self.uploaded_files["verification"] = file_path
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"File selected: {e.files[0].name}"))
            )
    
    def _encrypt_document(self, password: str):
        """Encrypt the uploaded document."""
        if "encryption" not in self.uploaded_files:
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
            file_path = self.uploaded_files["encryption"]
            output_path = file_path.replace(".", "_encrypted.")
            
            # Use the core encryptor
            result = self.encryptor.encrypt_file(
                input_file=file_path,
                output_file=output_path,
                password=password
            )
            
            if result.get("success"):
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"File encrypted successfully: {os.path.basename(output_path)}"),
                        action="OK"
                    )
                )
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Encryption failed: {result.get('error', 'Unknown error')}"),
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
        if "hashing" not in self.uploaded_files:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a file first"))
            )
            return
        
        try:
            file_path = self.uploaded_files["hashing"]
            
            # Use the core hash generator
            hash_value = self.hash_generator.generate_file_hash(file_path)
            
            if hash_value:
                # Save hash
                self.hash_generator.save_hash_to_file(file_path, hash_value, "original")
                
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Hash generated: {hash_value[:16]}..."),
                        action="OK"
                    )
                )
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Failed to generate hash"),
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
        if "verification" not in self.uploaded_files:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Please select a file first"))
            )
            return
        
        try:
            file_path = self.uploaded_files["verification"]
            
            # Use the core verifier
            result = self.verifier.verify_protected_document(file_path)
            
            if result.get("integrity_verified"):
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Document integrity verified successfully!"),
                        action="OK"
                    )
                )
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Verification failed: {result.get('error', 'Unknown error')}"),
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
    
    def _handle_route_change(self, route):
        """Handle route changes."""
        pass

def main():
    """Main entry point for the web application."""
    app = DocumentProtectionWebApp()
    ft.app(target=app.main, view=ft.WEB_BROWSER)

if __name__ == "__main__":
    main() 