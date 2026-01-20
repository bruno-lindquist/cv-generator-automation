#!/bin/bash
# Script to generate CV as PDF
# Automatically generates CV in Portuguese (PT) and English (EN)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect operating system
OS=$(uname -s)

# Function to activate venv
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

# Function to generate CV
generate_cv() {
    local lang=$1
    local lang_name=$2
    activate_venv
    
    PYTHON_CMD="./venv/bin/python"
    [ ! -f "$PYTHON_CMD" ] && PYTHON_CMD="python3"
    
    echo ""
    echo "$lang_name Generating CV in $lang_name..."
    "$PYTHON_CMD" cv_generator.py -l "$lang"
}

# Automatically generate both versions
echo ""
echo "========================================"
echo "   CV Generator - Automatic"
echo "========================================"

generate_cv "pt" "🇧🇷"
generate_cv "en" "🇬🇧"

echo ""
echo "✅ Both versions generated successfully!"
echo "========================================"
echo ""

