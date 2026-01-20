@echo off
REM Windows Script - CV Generator

REM Go to script directory
cd /d "%~dp0"

REM Create virtual environment if not exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    
    echo 📥 Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -q reportlab
    echo ✓ Setup complete!
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Interactive menu
echo.
echo 📋 CV Generator
echo ==================
echo 1) Portuguese
echo 2) English
echo 3) Both versions
echo.
set /p choice="Choose an option (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🇧🇷 Generating CV in Portuguese...
    python cv_generator.py
    echo.
) else if "%choice%"=="2" (
    echo.
    echo 🇬🇧 Generating CV in English...
    python cv_generator.py -l en
    echo.
) else if "%choice%"=="3" (
    echo.
    echo 🇧🇷 Generating CV in Portuguese...
    python cv_generator.py
    echo 🇬🇧 Generating CV in English...
    python cv_generator.py -l en
    echo ✅ Both versions generated!
    echo.
) else (
    echo ❌ Invalid option!
)
