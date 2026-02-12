#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${ROOT_DIR}"

echo "Iniciando limpeza do projeto em: ${ROOT_DIR}"
echo "Preservando ambiente virtual padrão: .venv"
echo

remove_dir_if_exists() {
  local dir_path="$1"
  if [ -d "${dir_path}" ]; then
    rm -rf "${dir_path}"
    echo "Removido diretório: ${dir_path}"
  fi
}

# Diretórios de artefatos comuns na raiz.
remove_dir_if_exists "./output"
remove_dir_if_exists "./logs"
remove_dir_if_exists "./build"
remove_dir_if_exists "./dist"
remove_dir_if_exists "./htmlcov"
remove_dir_if_exists "./.pytest_cache"

# Remove __pycache__ e *.egg-info fora de .venv/.git.
find . \
  \( -path "./.venv" -o -path "./.git" \) -prune \
  -o -type d \( -name "__pycache__" -o -name "*.egg-info" \) -print0 |
while IFS= read -r -d '' path; do
  rm -rf "${path}"
  echo "Removido diretório: ${path}"
done

# Remove arquivos temporários fora de .venv/.git.
find . \
  \( -path "./.venv" -o -path "./.git" \) -prune \
  -o -type f \
  \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" -o -name "Thumbs.db" -o -name "*.log" \) \
  -print0 |
while IFS= read -r -d '' file_path; do
  rm -f "${file_path}"
  echo "Removido arquivo: ${file_path}"
done

echo
echo "Limpeza concluída com sucesso."
echo "Pressione Enter para fechar..."
read -r _
