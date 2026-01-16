@echo off
REM Setup automático - Gerador de CV

cd /d "%~dp0"

echo.
echo 🚀 Setup Gerador de CV
echo =======================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo Instale Python de https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python encontrado:
python --version

REM Cria venv
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
    echo ✓ Ambiente virtual criado
) else (
    echo ✓ Ambiente virtual já existe
)

REM Ativa venv
call venv\Scripts\activate.bat

REM Instala dependências
echo 📥 Instalando dependências...
pip install -q reportlab
echo ✓ Dependências instaladas

REM Valida cv_data.json
echo ✓ Validando cv_data.json...
python -c "from cv_generator import CVGenerator; CVGenerator('cv_data.json')" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ cv_data.json com problemas (verifique e tente novamente)
) else (
    echo ✓ cv_data.json válido
)

echo.
echo ✅ Setup completo!
echo.
echo Próximos passos:
echo   1. Edite cv_data.json com seus dados
echo   2. Execute: cv.bat
echo.
pause
