@echo off
echo 🚀 Starting DocProject Web Server
echo ==================================================

REM Check if web directory exists
if not exist "web" (
    echo ❌ Error: web directory not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if index.html exists
if not exist "web\index.html" (
    echo ❌ Error: index.html not found in web directory!
    pause
    exit /b 1
)

echo ✅ Web directory and files found
echo 📁 Web directory: %CD%\web
echo 📄 Index file: %CD%\web\index.html

REM Change to web directory
cd web
echo 📁 Changed to directory: %CD%

echo.
echo 🌐 Starting web server on http://localhost:8080
echo 📋 Press Ctrl+C to stop the server
echo --------------------------------------------------

REM Start the Python HTTP server
python -m http.server 8080

echo.
echo 🛑 Server stopped
pause 