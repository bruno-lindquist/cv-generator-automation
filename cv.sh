#!/bin/bash
# Script para gerar CV em PDF
# Uso: ./cv.sh [idioma] ou ./cv.sh [todas] para ambos idiomas

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

OPTION="${1:-interactive}"

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
    activate_venv
    
    PYTHON_CMD="./venv/bin/python"
    [ ! -f "$PYTHON_CMD" ] && PYTHON_CMD="python3"
    
    "$PYTHON_CMD" cv_generator_new.py -l "$lang"
}

# Modo não-interativo
if [[ "$OPTION" == "pt" || "$OPTION" == "en" ]]; then
    generate_cv "$OPTION"
    exit $?
fi

if [[ "$OPTION" == "todas" || "$OPTION" == "both" ]]; then
    echo "🇧🇷 Gerando CV em português..."
    generate_cv pt
    echo ""
    echo "🇬🇧 Gerando CV em inglês..."
    generate_cv en
    echo ""
    echo "✅ Ambas as versões geradas!"
    exit 0
fi

# Modo interativo
echo ""
echo "📋 Gerador de CV"
echo "=================="
echo "1) Português (pt)"
echo "2) Inglês (en)"
echo "3) Ambas as versões"
echo ""
read -p "Escolha uma opção (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🇧🇷 Gerando CV em português..."
        generate_cv pt
        ;;
    2)
        echo ""
        echo "🇬🇧 Gerando CV em inglês..."
        generate_cv en
        ;;
    3)
        echo ""
        echo "🇧🇷 Gerando CV em português..."
        generate_cv pt
        echo "🇬🇧 Gerando CV em inglês..."
        generate_cv en
        echo "✅ Ambas as versões geradas!"
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

