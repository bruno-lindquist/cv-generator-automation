#!/bin/bash
set -euo pipefail

# Garante execução a partir da raiz do projeto, independente do diretório atual do terminal.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Arquivo monitorado no modo --watch.
CV_DATA_JSON_FILE_PATH="data/cv_data.json"

# Usa apenas o Python da venv do projeto para manter execução determinística.
PYTHON_EXECUTABLE_PATH="./.venv/bin/python"
[ -f "$PYTHON_EXECUTABLE_PATH" ] || { echo "Python da venv não encontrado em $PYTHON_EXECUTABLE_PATH"; exit 1; }

# Executa a geração para os dois idiomas suportados.
generate_cv_for_all_languages() {
    for language_code in pt en; do
        PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" "$PYTHON_EXECUTABLE_PATH" -c "from cv_service import run_generation; run_generation(config_file_path='config/config.json', language='${language_code}', input_file_path=None, output_file_path=None)"
    done
}

# Observa alterações no conteúdo do JSON e dispara nova geração quando houver mudança.
watch_cv_data_and_regenerate() {
    [ -f "$CV_DATA_JSON_FILE_PATH" ] || { echo "Arquivo não encontrado: $CV_DATA_JSON_FILE_PATH"; exit 1; }
    generate_cv_for_all_languages
    local previous_file_checksum current_file_checksum
    previous_file_checksum="$(cksum "$CV_DATA_JSON_FILE_PATH")"
    while sleep 1; do
        [ -f "$CV_DATA_JSON_FILE_PATH" ] || continue
        current_file_checksum="$(cksum "$CV_DATA_JSON_FILE_PATH")"
        [ "$current_file_checksum" = "$previous_file_checksum" ] && continue
        previous_file_checksum="$current_file_checksum"
        generate_cv_for_all_languages
    done
}

# Sem argumentos: executa uma vez. Com --watch: execução contínua por mudanças no JSON.
[ "${1:-}" = "--watch" ] && watch_cv_data_and_regenerate || generate_cv_for_all_languages
