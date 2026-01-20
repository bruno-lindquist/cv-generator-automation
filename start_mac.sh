#!/bin/bash
# Script para gerar CV em PDF
# Gera automaticamente CV em Português (PT) e Inglês (EN)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detecta o sistema operacional
OS=$(uname -s)

# Função para ativar venv
activate_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        case "$OS" in
            Darwin|Linux)
                source venv/bin/activate 2>/dev/null || true
                ;;
            MINGW*|MSYS*|CYGWIN*)
                source venv/Scripts/activate 2>/dev/null || true
                ;;
        esac
    fi
}

# Função para gerar CV
generate_cv() {
    local lang=$1
    local lang_name=$2
    activate_venv
    
    PYTHON_CMD="./venv/bin/python"
    [ ! -f "$PYTHON_CMD" ] && PYTHON_CMD="python3"
    
    echo ""
    echo "$lang_name Gerando CV em $lang_name..."
    "$PYTHON_CMD" cv_generator.py -l "$lang"
}

# Gera automaticamente ambas as versões
echo ""
echo "========================================"
echo "   Gerador de CV - Automático"
echo "========================================"

generate_cv "pt" "🇧🇷"
generate_cv "en" "🇬🇧"

echo ""
echo "✅ Ambas as versões geradas com sucesso!"
echo "========================================"
echo ""

