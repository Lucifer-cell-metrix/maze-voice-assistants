@echo off
echo ═══════════════════════════════════════
echo   MAZE — AI Assistant (Starting...)
echo ═══════════════════════════════════════
echo.

:: Use venv Python so all packages are found
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py
) else (
    echo [!] Virtual environment not found.
    echo [!] Run: python -m venv venv
    echo [!] Then: venv\Scripts\pip install -r requirements.txt
    pause
)
