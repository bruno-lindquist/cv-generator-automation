#!/bin/bash
# Gera o CV em PDF nas versões PT e EN

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Gera o CV para o idioma informado.
# Ordem de tentativa:
# 1) executável local em .venv/bin (Unix);
# 2) executável local em .venv/Scripts (Windows);
# 3) comando global cv-generator no PATH;
# 4) execução do módulo CLI com Python.
generate_cv() {
    local lang=$1
    local lang_flag=$2

    printf '\n%s Gerando CV em %s...\n' "$lang_flag" "$lang"
    if [ -x "./.venv/bin/cv-generator" ]; then
        # Prioriza o binário do projeto para garantir versão consistente
        "./.venv/bin/cv-generator" -l "$lang"
        return
    fi

    if [ -x "./.venv/Scripts/cv-generator" ]; then
        # Compatibilidade com estrutura de venv no Windows
        "./.venv/Scripts/cv-generator" -l "$lang"
        return
    fi

    if command -v "cv-generator" >/dev/null 2>&1; then
        # Usa a instalação global apenas quando não houver binário local do projeto
        cv-generator -l "$lang"
        return
    fi

    # Fallback final via Python, preservando imports locais em src
    PYTHON_CMD="./.venv/bin/python"
    [ ! -f "$PYTHON_CMD" ] && PYTHON_CMD="./.venv/Scripts/python.exe"
    [ ! -f "$PYTHON_CMD" ] && PYTHON_CMD="python3"
    PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_CMD" -m cli -l "$lang"
}

# Executa a geração para os dois idiomas suportados
printf '\n'
echo "========================================"
echo "             CV Generator"
echo "========================================"

for lang in pt en; do
    # Associa cada idioma à bandeira exibida no log
    case "$lang" in
        pt) flag="🇧🇷" ;;
        en) flag="🇬🇧" ;;
    esac

    generate_cv "$lang" "$flag"
done

#generate_cv "pt" "🇧🇷"

printf '\n'
echo "✅ Both versions generated successfully!"
echo "========================================"
printf '\n'
