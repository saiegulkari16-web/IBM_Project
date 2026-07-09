Set-Location $PSScriptRoot

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found." -ForegroundColor Red
    Write-Host "Run setup first or ask Codex to recreate the venv."
    Read-Host "Press Enter to close"
    exit 1
}

Write-Host "Starting Money Matters..." -ForegroundColor Cyan
Write-Host "Open http://127.0.0.1:8501 after the server starts." -ForegroundColor Yellow
Write-Host ""

& ".\venv\Scripts\python.exe" -m streamlit run frontend/app.py

Write-Host ""
Write-Host "The app stopped or failed to start." -ForegroundColor Red
Read-Host "Press Enter to close"
