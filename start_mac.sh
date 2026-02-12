#!/bin/bash
# Script to generate CV as PDF
# Automatically generates CV in Portuguese (PT) and English (EN)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect operating system
OS=$(uname -s)

# Function to activate virtual environment
activate_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        case "$OS" in
            Darwin|Linux)
                source .venv/bin/activate 2>/dev/null || true
                ;;
            MINGW*|MSYS*|CYGWIN*)
                source .venv/Scripts/activate 2>/dev/null || true
                ;;
        esac
    fi
}

# Function to generate CV
generate_cv() {
    local lang=$1
    local lang_name=$2
    activate_venv

    echo ""
    echo "$lang_name Generating CV in $lang_name..."
    if [ -x "./.venv/bin/cv-generator" ]; then
        "./.venv/bin/cv-generator" -l "$lang"
        return
    fi

    if command -v "cv-generator" >/dev/null 2>&1; then
        cv-generator -l "$lang"
        return
    fi

    PYTHON_CMD="./.venv/bin/python"
    [ ! -f "$PYTHON_CMD" ] && PYTHON_CMD="python3"
    PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_CMD" -m cli -l "$lang"
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
