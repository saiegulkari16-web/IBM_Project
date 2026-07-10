@echo off
setlocal

cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
  echo Virtual environment not found.
  echo Run setup first or tell Codex to recreate the venv.
  pause
  exit /b 1
)

echo Starting Money Matters...
echo Open http://127.0.0.1:8501 after the server starts.
echo.

".\venv\Scripts\python.exe" -m streamlit run frontend/app.py

echo.
echo The app stopped or failed to start.
pause
