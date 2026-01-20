@echo off
REM Automatic Setup - CV Generator

cd /d "%~dp0"

echo.
echo 🚀 CV Generator Setup
echo =====================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Install Python from https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python found:
python --version

REM Create venv
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q reportlab
echo ✓ Dependencies installed

REM Validate cv_data.json
echo ✓ Validating cv_data.json...
python -c "from cv_generator import CVGenerator; CVGenerator('cv_data.json')" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ cv_data.json has issues (verify and try again)
) else (
    echo ✓ cv_data.json valid
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo   1. Edit cv_data.json with your data
echo   2. Execute: start_windows.bat
echo.
pause
