#!/bin/bash
set -euo pipefail

# Garante execução a partir da raiz do projeto, independente do diretório atual do terminal.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Arquivo monitorado no modo --watch.
CV_DATA_JSON_FILE_PATH="data/cv_data.json"

# Usa apenas o Python da venv do projeto para manter execução determinística.
PYTHON_EXECUTABLE_PATH="./.venv/bin/python"
[ -f "$PYTHON_EXECUTABLE_PATH" ] || { echo "Python da venv não encontrado em $PYTHON_EXECUTABLE_PATH"; exit 1; }

# Executa a geração para os dois idiomas suportados e ecoa a pasta do PDF gerado.
generate_cv_for_all_languages() {
    local last_output_directory=""
    for language_code in pt en; do
        last_output_directory="$(PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_EXECUTABLE_PATH" -c "from cv_service import run_generation; generated_path = run_generation(config_file_path='config/config.json', language='${language_code}', input_file_path=None, output_file_path=None); print(generated_path.parent)")"
    done
    printf '%s\n' "$last_output_directory"
}

# Abre no Finder/Explorer a pasta onde os PDFs foram salvos.
open_output_directory() {
    local directory_path="$1"
    [ -n "$directory_path" ] || return 0
    [ -d "$directory_path" ] || return 0
    case "$OSTYPE" in
        darwin*) open -a Finder "$directory_path" ;;
        linux*) xdg-open "$directory_path" >/dev/null 2>&1 ;;
        msys*|cygwin*|win32*) explorer "$directory_path" ;;
    esac
}

# Observa alterações no conteúdo do JSON e dispara nova geração quando houver mudança.
watch_cv_data_and_regenerate() {
    [ -f "$CV_DATA_JSON_FILE_PATH" ] || { echo "Arquivo não encontrado: $CV_DATA_JSON_FILE_PATH"; exit 1; }
    local output_directory
    output_directory="$(generate_cv_for_all_languages)"
    open_output_directory "$output_directory"
    local previous_file_checksum current_file_checksum
    previous_file_checksum="$(cksum "$CV_DATA_JSON_FILE_PATH")"
    while sleep 1; do
        [ -f "$CV_DATA_JSON_FILE_PATH" ] || continue
        current_file_checksum="$(cksum "$CV_DATA_JSON_FILE_PATH")"
        [ "$current_file_checksum" = "$previous_file_checksum" ] && continue
        previous_file_checksum="$current_file_checksum"
        # Modo watch: nao reabre a pasta a cada mudanca para nao interromper a edicao.
        generate_cv_for_all_languages >/dev/null
    done
}

# Execucao unica: gera e abre a pasta dos PDFs ao terminar.
run_once_and_open() {
    local output_directory
    output_directory="$(generate_cv_for_all_languages)"
    open_output_directory "$output_directory"
}

# Sem argumentos: executa uma vez. Com --watch: execução contínua por mudanças no JSON.
[ "${1:-}" = "--watch" ] && watch_cv_data_and_regenerate || run_once_and_open
