# DocProject Web Server - PowerShell Script
Write-Host "🚀 Starting DocProject Web Server" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

# Check if web directory exists
if (-not (Test-Path "web")) {
    Write-Host "❌ Error: web directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if index.html exists
if (-not (Test-Path "web\index.html")) {
    Write-Host "❌ Error: index.html not found in web directory!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Web directory and files found" -ForegroundColor Green
Write-Host "📁 Web directory: $((Get-Location).Path)\web" -ForegroundColor Cyan
Write-Host "📄 Index file: $((Get-Location).Path)\web\index.html" -ForegroundColor Cyan

# Change to web directory
Set-Location "web"
Write-Host "📁 Changed to directory: $(Get-Location)" -ForegroundColor Cyan

Write-Host ""
Write-Host "🌐 Starting web server on http://localhost:8080" -ForegroundColor Green
Write-Host "📋 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "--------------------------------------------------" -ForegroundColor Cyan

# Start the Python HTTP server
try {
    python -m http.server 8080
}
catch {
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
}
finally {
    Write-Host ""
    Write-Host "🛑 Server stopped" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
} 