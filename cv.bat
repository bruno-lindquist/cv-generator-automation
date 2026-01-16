@echo off
REM Script para Windows - Gerador de CV

REM Vai para o diretório do script
cd /d "%~dp0"

REM Cria virtual environment se não existir
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    
    echo 📥 Instalando dependências...
    call venv\Scripts\activate.bat
    pip install -q reportlab
    echo ✓ Setup completo!
)

REM Ativa o virtual environment
call venv\Scripts\activate.bat

REM Menu interativo
echo.
echo 📋 Gerador de CV
echo ==================
echo 1) Português
echo 2) Inglês
echo 3) Ambas as versões
echo.
set /p choice="Escolha uma opção (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🇧🇷 Gerando CV em português...
    python cv_generator.py
    echo.
) else if "%choice%"=="2" (
    echo.
    echo 🇬🇧 Gerando CV em inglês...
    python cv_generator.py -l en
    echo.
) else if "%choice%"=="3" (
    echo.
    echo 🇧🇷 Gerando CV em português...
    python cv_generator.py
    echo 🇬🇧 Gerando CV em inglês...
    python cv_generator.py -l en
    echo ✅ Ambas as versões geradas!
    echo.
) else (
    echo ❌ Opção inválida!
)
