import flet as ft
import os
from core.steganography import DocumentSteganography
import json
from pathlib import Path
from core.encryptor import DocumentEncryptor
from core.hash_generator import HashGenerator

# Entry point for the Flet app
def main(page: ft.Page):
    page.title = "DocProject - Document Processor"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT

    # State for dropped files
    dropped_files = []

    def on_drop(event: ft.DragTargetAcceptEvent):
        files = [f.path for f in event.files]
        dropped_files.extend(files)
        # Update output list
        output_list = page.controls[0].controls[2].controls[1]
        for file in files:
            output_list.controls.append(ft.Text(file))
        output_list.update()
        # Show snackbar
        page.snack_bar = ft.SnackBar(ft.Text(f"{len(files)} file(s) dropped."))
        page.snack_bar.open = True
        page.update()

    # Create FilePicker instances for files and folders
    file_picker = ft.FilePicker()
    folder_picker = ft.FilePicker()
    page.overlay.extend([file_picker, folder_picker])

    def get_output_list():
        # The structure is: Tabs -> Protect Tab (index 0) -> Column -> file_select, progress_section, output_section (index 2)
        # output_section: Column([Text, Card]), expand=True
        # Card: content=Container(content=Column([ListView], expand=True))
        # So: page.controls[0] (Tabs), .tabs[0] (Protect), .content (Column), .controls[2] (output_section), .controls[1] (Card), .content (Container), .content (Column), .controls[0] (ListView)
        tabs = page.controls[0]
        protect_tab = tabs.tabs[0]
        protect_col = protect_tab.content
        output_section = protect_col.controls[2]
        card = output_section.controls[1]
        container = card.content
        col = container.content
        return col.controls[0]

    def on_choose_files(e):
        def files_chosen(result):
            if result.files:
                for f in result.files:
                    dropped_files.append(f.path)
                    get_output_list().controls.append(ft.Text(f.path))
                get_output_list().update()
                page.snack_bar = ft.SnackBar(ft.Text(f"{len(result.files)} file(s) selected."))
                page.snack_bar.open = True
                page.update()
        file_picker.on_result = files_chosen
        file_picker.pick_files(allow_multiple=True)

    def on_choose_folder(e):
        def folder_chosen(result):
            if result.path:
                folder_path = result.path
                files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                for f in files:
                    dropped_files.append(f)
                    get_output_list().controls.append(ft.Text(f))
                get_output_list().update()
                page.snack_bar = ft.SnackBar(ft.Text(f"{len(files)} file(s) selected from folder."))
                page.snack_bar.open = True
                page.update()
        folder_picker.on_result = folder_chosen
        folder_picker.pick_folder()

    encryptor = DocumentEncryptor()

    encrypt_checkbox = ft.Checkbox(label="Encrypt Payload", value=False)
    password_field = ft.TextField(label="Encryption Password", password=True, visible=False)

    def on_encrypt_toggle(e):
        password_field.visible = encrypt_checkbox.value
        page.update()
    encrypt_checkbox.on_change = on_encrypt_toggle

    def process_files(e):
        if not dropped_files:
            page.snack_bar = ft.SnackBar(ft.Text("No files selected for processing."))
            page.snack_bar.open = True
            page.update()
            return
        output_list = get_output_list()
        output_list.controls.clear()
        steg = DocumentSteganography()
        hash_gen = HashGenerator()
        total = len(dropped_files)
        # Use user-provided secret data
        user_secret = secret_data_field.value.encode('utf-8') if secret_data_field.value else b"Hidden integrity payload"
        for idx, file_path in enumerate(dropped_files):
            ext = os.path.splitext(file_path)[1].lower()
            # Set output and hash paths
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                output_file = os.path.join("data", "output", base_name + "_protected.png")
            elif ext == ".pdf":
                output_file = os.path.join("data", "output", base_name + "_protected.pdf")
            elif ext in [".xlsx", ".xls", ".csv"]:
                output_file = str(Path(file_path).with_stem(Path(file_path).stem + "_protected"))
            else:
                output_file = os.path.join("data", "output", base_name + "_protected" + ext)

            # Generate original hash
            original_hash = hash_gen.generate_file_hash(file_path)
            result = None
            if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                result = steg.hide_data_in_image(file_path, user_secret, output_file, original_hash=original_hash)
                # After protection, generate protected hash
                if result and result.get('success'):
                    protected_hash = hash_gen.generate_file_hash(result['stego_image'])
                    result['protected_hash'] = protected_hash
                    # Save hashes
                    hash_gen.save_hash_to_file(file_path, original_hash, hash_type="original")
                    hash_gen.save_hash_to_file(result['stego_image'], protected_hash, hash_type="protected")
            elif ext == ".pdf":
                # Step 1: Hide with original hash only
                result = steg.hide_data_in_pdf(file_path, user_secret, output_file, original_hash=original_hash)
                if result and result.get('success'):
                    # Step 2: Generate protected hash
                    protected_hash = hash_gen.generate_file_hash(result['stego_document'])
                    result['protected_hash'] = protected_hash
                    # Step 3: Rewrite PDF with protected hash in metadata
                    result2 = steg.hide_data_in_pdf(file_path, user_secret, output_file, original_hash=original_hash, protected_hash=protected_hash)
                    if result2 and result2.get('success'):
                        # Overwrite output_file with correct protected hash
                        protected_hash = hash_gen.generate_file_hash(result2['stego_document'])
                        result['protected_hash'] = protected_hash
                        hash_gen.save_hash_to_file(file_path, original_hash, hash_type="original")
                        hash_gen.save_hash_to_file(result2['stego_document'], protected_hash, hash_type="protected")
                    else:
                        msg = f"Failed to embed protected hash in PDF: {result2.get('error', 'Unknown error') if result2 else 'Unknown error'}"
                        color = "red"
                        output_list.controls.append(ft.Text(msg, color=color))
                        continue
            elif ext in [".xlsx", ".xls", ".csv"]:
                result = steg.hide_data_in_excel(file_path, user_secret, output_file)
                if result and result.get('success'):
                    protected_hash = hash_gen.generate_file_hash(output_file)
                    result['protected_hash'] = protected_hash
                    hash_gen.save_hash_to_file(file_path, original_hash, hash_type="original")
                    hash_gen.save_hash_to_file(output_file, protected_hash, hash_type="protected")
            else:
                # Add other file type logic here as needed (existing logic)
                result = None
            if result and result.get('success'):
                msg = f"Protected: {file_path} -> {output_file}\nMethod: {result.get('method', 'unknown')}"
                color = "green"
            else:
                if result is not None:
                    error_msg = result.get('error', 'Unknown error')
                else:
                    error_msg = 'Unknown error (no result returned)'
                msg = f"Failed: {file_path}\nError: {error_msg}"
                color = "red"
            output_list.controls.append(ft.Text(msg, color=color))
            progress = int(((idx + 1) / total) * 100)
            progress_section.controls[1].value = progress / 100
            progress_section.controls[2].value = f"{progress}% complete"
            output_list.update()
            page.update()
        progress_section.controls[2].value = "Processing complete."
        page.snack_bar = ft.SnackBar(ft.Text("Processing complete."))
        page.snack_bar.open = True
        page.update()

    # Insert encryption controls into file_select
    file_select = ft.Column([
        ft.Text("Select files or drag-and-drop here:", size=18, weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("Choose Files", icon=ft.icons.UPLOAD_FILE),
        ft.DragTarget(
            content=ft.Container(
                content=ft.Text("Drag files or folders here", size=16, italic=True),
                width=400,
                height=80,
                bgcolor=ft.colors.GREY_200,
                border=ft.border.all(2, ft.colors.BLUE_200),
                alignment=ft.alignment.center,
            ),
            on_accept=on_drop,
        ),
        ft.ElevatedButton("Choose Folder (Batch)", icon=ft.icons.FOLDER),
        ft.Container(height=40),
    ])
    file_select.controls[1].on_click = on_choose_files
    file_select.controls[3].on_click = on_choose_folder
    file_select.controls.append(encrypt_checkbox)
    file_select.controls.append(password_field)

    progress_section = ft.Column([
        ft.Text("Progress:", size=16, weight=ft.FontWeight.BOLD),
        ft.ProgressBar(width=400, value=0, color="blue"),
        ft.Text("No processing yet.", key="progress_text"),
    ])

    output_section = ft.Column([
        ft.Text("Output:", size=16, weight=ft.FontWeight.BOLD),
        ft.ListView(expand=1, spacing=10, padding=10, key="output_list"),
    ], expand=True)

    # --- Secret Data Input for Protect Tab ---
    secret_data_field = ft.TextField(label="Secret Data to Embed", multiline=True, min_lines=2, max_lines=5)
    secret_file_btn = ft.ElevatedButton("Choose Secret Data File", icon=ft.icons.ATTACH_FILE)
    secret_file_path = [None]
    def on_choose_secret_file(e):
        def file_chosen(result):
            if result.files:
                secret_file_path[0] = result.files[0].path
                # Use 'r' mode for text field
                with open(secret_file_path[0], 'r', encoding='utf-8', errors='ignore') as f:
                    secret_data_field.value = f.read()
                page.snack_bar = ft.SnackBar(ft.Text(f"Loaded secret data from {secret_file_path[0]}"))
                page.snack_bar.open = True
                page.update()
        file_picker.on_result = file_chosen
        file_picker.pick_files(allow_multiple=False)
    secret_file_btn.on_click = on_choose_secret_file
    file_select.controls.insert(4, secret_data_field)
    file_select.controls.insert(5, secret_file_btn)

    # Add Process button
    process_btn = ft.ElevatedButton("Process", icon=ft.icons.PLAY_ARROW, on_click=process_files)
    file_select.controls.append(process_btn)

    # --- Verification Tab ---
    verify_files = []
    verify_output_list = ft.ListView(expand=1, spacing=10, padding=10)
    verify_progress = ft.ProgressBar(width=400, value=0, color="green")
    verify_status = ft.Text("No verification yet.")

    def on_verify_drop(event: ft.DragTargetAcceptEvent):
        files = [f.path for f in event.files]
        verify_files.extend(files)
        for file in files:
            verify_output_list.controls.append(ft.Text(f"Selected: {file}"))
        verify_output_list.update()
        page.snack_bar = ft.SnackBar(ft.Text(f"{len(files)} file(s) added for verification."))
        page.snack_bar.open = True
        page.update()

    def on_verify_choose_files(e):
        def files_chosen(result):
            if result.files:
                for f in result.files:
                    verify_files.append(f.path)
                    verify_output_list.controls.append(ft.Text(f"Selected: {f.path}"))
                verify_output_list.update()
                page.snack_bar = ft.SnackBar(ft.Text(f"{len(result.files)} file(s) selected for verification."))
                page.snack_bar.open = True
                page.update()
        file_picker.on_result = files_chosen
        file_picker.pick_files(allow_multiple=True)

    def verify_documents(e):
        if not verify_files:
            page.snack_bar = ft.SnackBar(ft.Text("No files selected for verification."))
            page.snack_bar.open = True
            page.update()
            return
        verify_output_list.controls.clear()
        steg = DocumentSteganography()
        hash_gen = HashGenerator()
        total = len(verify_files)
        for idx, file_path in enumerate(verify_files):
            ext = os.path.splitext(file_path)[1].lower()
            result = None
            msg = ""
            color = "red"
            if ext in [".xlsx", ".xls", ".csv"]:
                result = steg.extract_data_from_excel(file_path)
                if result.get('success'):
                    msg = f"Extracted from: {file_path}\nMethod: {result.get('method', 'unknown')}\nMetadata: {result.get('metadata', {})}"
                    color = "green"
                else:
                    msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
            elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                result = steg.extract_data_from_image(file_path)
                if result.get('success'):
                    current_hash = hash_gen.generate_file_hash(file_path)
                    stored_hash = hash_gen.load_hash_from_file(file_path, hash_type="protected")
                    match = (current_hash == stored_hash)
                    msg = f"Verified: {file_path}\nStatus: {'VERIFIED' if match else 'NOT VERIFIED'}\nCurrent Hash: {current_hash}\nStored Hash: {stored_hash}"
                    color = "green" if match else "orange"
                else:
                    msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
            elif ext == ".pdf":
                result = steg.extract_data_from_pdf(file_path)
                if result.get('success'):
                    current_hash = hash_gen.generate_file_hash(file_path)
                    stored_hash = hash_gen.load_hash_from_file(file_path, hash_type="protected")
                    match = (current_hash == stored_hash)
                    msg = f"Verified: {file_path}\nStatus: {'VERIFIED' if match else 'NOT VERIFIED'}\nCurrent Hash: {current_hash}\nStored Hash: {stored_hash}"
                    color = "green" if match else "orange"
                else:
                    msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
            else:
                msg = f"Verification not supported for: {file_path}"
            verify_output_list.controls.append(ft.Text(msg, color=color))
            progress = int(((idx + 1) / total) * 100)
            verify_progress.value = progress / 100
            verify_status.value = f"{progress}% complete"
            verify_output_list.update()
            page.update()
        verify_status.value = "Verification complete."
        page.snack_bar = ft.SnackBar(ft.Text("Verification complete."))
        page.snack_bar.open = True
        page.update()

    verify_drag_target = ft.DragTarget(
        content=ft.Container(
            content=ft.Text("Drag files here for verification", size=16, italic=True),
            width=400,
            height=80,
            bgcolor=ft.colors.GREY_200,
            border=ft.border.all(2, ft.colors.GREEN_200),
            alignment=ft.alignment.center,
        ),
        on_accept=on_verify_drop,
    )
    verify_btn = ft.ElevatedButton("Choose Files", icon=ft.icons.UPLOAD_FILE, on_click=on_verify_choose_files)
    verify_process_btn = ft.ElevatedButton("Verify", icon=ft.icons.VERIFIED, on_click=verify_documents)

    verify_tab = ft.Column([
        ft.Text("Document Verification", size=18, weight=ft.FontWeight.BOLD),
        verify_btn,
        verify_drag_target,
        verify_process_btn,
        verify_progress,
        verify_status,
        verify_output_list,
    ], expand=True, spacing=20)

    # --- UI/UX Polish ---
    # Enhanced drag target with hover effect
    def drag_target_style(is_hovered):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.DRIVE_FOLDER_UPLOAD, size=32, color=ft.colors.BLUE_400),
                ft.Text("Drag files or folders here", size=16, italic=True),
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=420,
            height=90,
            bgcolor=ft.colors.BLUE_50 if is_hovered else ft.colors.GREY_200,
            border=ft.border.all(2, ft.colors.BLUE_400 if is_hovered else ft.colors.BLUE_200),
            border_radius=10,
            alignment=ft.alignment.center,
            padding=10,
        )

    # Enhanced output section with Card
    output_section = ft.Column([
        ft.Text("Output:", size=16, weight=ft.FontWeight.BOLD),
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListView(expand=1, spacing=10, padding=10, key="output_list"),
                ], expand=True),
                padding=10,
                bgcolor=ft.colors.WHITE,
            ),
            elevation=3,
        ),
    ], expand=True)

    # Enhanced progress section
    progress_section = ft.Column([
        ft.Text("Progress:", size=16, weight=ft.FontWeight.BOLD),
        ft.ProgressBar(width=400, value=0, color="blue"),
        ft.Text("No processing yet.", key="progress_text"),
    ], spacing=10)

    # Enhanced file_select with tooltips and spacing
    file_select.controls[1].tooltip = "Select one or more files to protect"
    file_select.controls[3].tooltip = "Select a folder for batch protection"
    process_btn.tooltip = "Start protection for all selected files"
    encrypt_checkbox.tooltip = "Encrypt the embedded payload for extra security"
    password_field.tooltip = "Password used for encryption (if enabled)"
    file_select.spacing = 12

    # --- Enhanced Verification Tab ---
    def verify_drag_target_style(is_hovered):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.DRIVE_FOLDER_UPLOAD, size=32, color=ft.colors.GREEN_400),
                ft.Text("Drag files here for verification", size=16, italic=True),
            ], alignment=ft.MainAxisAlignment.CENTER),
            width=420,
            height=90,
            bgcolor=ft.colors.GREEN_50 if is_hovered else ft.colors.GREY_200,
            border=ft.border.all(2, ft.colors.GREEN_400 if is_hovered else ft.colors.GREEN_200),
            border_radius=10,
            alignment=ft.alignment.center,
            padding=10,
        )
    verify_drag_hovered = [False]
    def on_verify_drag_enter(e):
        verify_drag_hovered[0] = True
        verify_drag_target.content = verify_drag_target_style(True)
        page.update()
    def on_verify_drag_leave(e):
        verify_drag_hovered[0] = False
        verify_drag_target.content = verify_drag_target_style(False)
        page.update()
    verify_drag_target.content = verify_drag_target_style(False)
    verify_drag_target.on_enter = on_verify_drag_enter
    verify_drag_target.on_leave = on_verify_drag_leave

    # Enhanced verification output with Card
    verify_output_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                verify_output_list,
            ], expand=True),
            padding=10,
            bgcolor=ft.colors.WHITE,
        ),
        elevation=3,
    )

    # Enhanced verification progress section
    verify_progress_section = ft.Column([
        ft.Text("Progress:", size=16, weight=ft.FontWeight.BOLD),
        verify_progress,
        verify_status,
    ], spacing=10)

    # Enhanced verify_tab layout
    verify_tab = ft.Column([
        ft.Text("Document Verification", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([
            verify_btn,
            verify_process_btn,
        ], spacing=10),
        verify_drag_target,
        verify_progress_section,
        verify_output_card,
    ], expand=True, spacing=20)

    # --- Tabs Layout (unchanged) ---
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Protect", content=ft.Column([
                file_select,
                progress_section,
                output_section,
            ], expand=True, spacing=30)),
            ft.Tab(text="Verify", content=verify_tab),
        ],
        expand=True,
    )
    page.controls.clear()
    page.add(tabs)

    # --- Extraction/Batch Extraction in Verify Tab ---
    extract_output_list = ft.ListView(expand=1, spacing=10, padding=10)
    def extract_payloads(e):
        if not verify_files:
            page.snack_bar = ft.SnackBar(ft.Text("No files selected for extraction."))
            page.snack_bar.open = True
            page.update()
            return
        extract_output_list.controls.clear()
        steg = DocumentSteganography()
        total = len(verify_files)
        for idx, file_path in enumerate(verify_files):
            ext = os.path.splitext(file_path)[1].lower()
            result = None
            if ext in [".xlsx", ".xls", ".csv"]:
                result = steg.extract_data_from_excel(file_path)
            # Add other file type logic here as needed (existing logic)
            if result and result.get('success'):
                payload = result.get('secret_data', b'').decode(errors='ignore')
                hashes = f"Original Hash: {result.get('original_hash')}\nProtected Hash: {result.get('protected_hash')}"
                match = (result.get('original_hash') == result.get('protected_hash'))
                msg = f"Extracted from: {file_path}\nPayload: {payload}\n{hashes}\nHashes Match: {'YES' if match else 'NO'}"
                color = "green" if match else "orange"
            else:
                msg = f"Failed: {file_path}\nError: {result.get('error', 'Unknown error')}"
                color = "red"
            extract_output_list.controls.append(ft.Text(msg, color=color))
            extract_output_list.update()
            page.update()
        page.snack_bar = ft.SnackBar(ft.Text("Extraction complete."))
        page.snack_bar.open = True
        page.update()
    extract_btn = ft.ElevatedButton("Extract Payload(s)", icon=ft.icons.DOWNLOAD, on_click=extract_payloads)
    # Add extraction output to verify_tab
    verify_tab.controls.append(extract_btn)
    verify_tab.controls.append(extract_output_list)

ft.app(target=main) 