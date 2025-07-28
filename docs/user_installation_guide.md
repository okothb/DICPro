# DocProject User Installation Guide

Welcome to DocProject! This guide will help you install and run the DocProject desktop application on Windows, Mac, or Linux.

---

## Prerequisites
- **Python 3.8+** must be installed. [Download Python](https://www.python.org/downloads/)
- **pip** (Python package manager) should be available in your PATH.
- (Optional) **Git** for cloning the repository.

---

## 1. Download or Clone the Project
- **Download ZIP:**
  1. Go to the project repository.
  2. Click "Code" > "Download ZIP" and extract it.
- **Or Clone with Git:**
  ```bash
  git clone <your-repo-url>
  cd DocProject
  ```

---

## 2. Install Dependencies
Open a terminal (Command Prompt, PowerShell, or Terminal) in the project folder and run:
```bash
pip install -r requirements.txt
pip install flet pyinstaller
```

---

## 3. Run the App (Development Mode)
To test the app before packaging:
```bash
python app.py
```

---

## 4. Package the App (Optional)
To create a standalone executable:
- **Windows:**
  - Run `package_app.bat` or:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --icon=DocPro.ico app.py
    ```
- **Mac/Linux:**
  - Run `bash package_app.sh` or:
    ```bash
    pyinstaller --noconfirm --onefile --windowed --icon=DocPro.ico app.py
    ```
- The packaged app will be in the `dist/` folder.

---

## 5. Install and Run the Packaged App
- **Windows:** Double-click `dist\app.exe`.
- **Mac/Linux:** Run `./dist/app` from the terminal.

---

## 6. Troubleshooting
- **Missing Python:** Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/).
- **pip not found:** Add Python to your PATH or reinstall Python.
- **Permission errors:** Try running the terminal as administrator (Windows) or use `sudo` (Mac/Linux).
- **App won’t start:** Ensure all dependencies are installed and you’re using the correct Python version.

---

## 7. Uninstallation
- To remove the app, simply delete the `dist/` folder and the project directory.

---

## 8. Need Help?
- Check the [README.md](../README.md) for more details.
- Contact the project maintainer for support.

--- 