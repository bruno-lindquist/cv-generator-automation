#!/bin/bash

# Setup automático - Gerador de CV

cd "$(dirname "$0")"

echo ""
echo "🚀 Setup Gerador de CV"
echo "======================="
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Instale Python 3 de https://www.python.org"
    exit 1
fi

echo "✓ Python 3 encontrado: $(python3 --version)"

# Cria venv
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✓ Ambiente virtual criado"
else
    echo "✓ Ambiente virtual já existe"
fi

# Ativa venv
source venv/bin/activate

# Instala dependências
echo "📥 Instalando dependências..."
pip install -q reportlab
echo "✓ Dependências instaladas"

# Valida cv_data.json
echo "✓ Validando cv_data.json..."
python3 -c "from cv_generator import CVGenerator; CVGenerator('cv_data.json')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ cv_data.json válido"
else
    echo "⚠️  cv_data.json com problemas (verifique e tente novamente)"
fi

echo ""
echo "✅ Setup completo!"
echo ""
echo "Próximos passos:"
echo "  1. Edite cv_data.json com seus dados"
echo "  2. Execute: ./cv.sh"
echo ""
