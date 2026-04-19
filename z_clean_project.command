#!/usr/bin/env bash
set -euo pipefail

# Define uma raiz fixa: a pasta onde este script está salvo.
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd -P)"

# Sempre preserva diretorios criticos.
PROTECTED_RELATIVE_PATHS=(
  ".git"
  ".venv"
)

# Nomes de diretorio que geralmente representam artefatos de execucao/build.
ROOT_LEVEL_DIRECTORIES=(
 # "__output"
  "out"
  "build"
  "dist"
  "htmlcov"
  "logs"
  "tmp"
  "temp"
  "coverage"
)

# Diretorios de cache/transientes que podem existir em qualquer profundidade.
GLOBAL_DIRECTORY_PATTERNS=(
  "__pycache__"
  "*.egg-info"
  ".pytest_cache"
  ".mypy_cache"
  ".ruff_cache"
  ".hypothesis"
  ".tox"
  ".nox"
  ".pyre"
  ".pytype"
  ".ipynb_checkpoints"
  ".parcel-cache"
  ".sass-cache"
  ".turbo"
  ".cache-loader"
)

# Arquivos temporarios/comuns de execucao.
GLOBAL_FILE_PATTERNS=(
  "*.pyc"
  "*.pyo"
  "*.pyd"
  ".coverage"
  ".coverage.*"
  "coverage.xml"
  "nosetests.xml"
  "pytestdebug.log"
  ".DS_Store"
  "Thumbs.db"
  "Desktop.ini"
  "*.tmp"
  "*.temp"
  "*.bak"
  "*.swp"
  "*.swo"
  "*.pid"
  ".eslintcache"
  "npm-debug.log*"
  "yarn-debug.log*"
  "pnpm-debug.log*"
)

PROTECTED_FIND_PRUNE_ARGS=()
CANDIDATE_REGISTRY_FILE=""
DELETION_CANDIDATES=()
COMPACTED_CANDIDATES=()

# Exibe ajuda resumida de uso e garantias de segurança.
print_usage() {
  cat <<'EOF'
Uso:
  limpar_projeto.command

Comportamento:
  1) Lista tudo que sera removido
  2) Exige confirmacao textual explicita
  3) So entao executa a limpeza

Seguranca:
  - Nunca remove .git e .venv
  - Limpa somente a pasta onde este script esta salvo
  - Nunca remove fora dessa raiz fixa
EOF
}

# Resolve caminho absoluto/canônico sem perder o nome final de arquivos.
resolve_existing_path() {
  local path="$1"
  local parent_dir
  local base_name

  # Diretórios podem ser resolvidos diretamente.
  if [ -d "$path" ]; then
    (cd "$path" 2>/dev/null && pwd -P) || return 1
    return 0
  fi

  # Para arquivos, resolve o diretório pai e recompõe o caminho.
  parent_dir="$(cd "$(dirname "$path")" 2>/dev/null && pwd -P)" || return 1
  base_name="$(basename "$path")"
  printf '%s/%s\n' "$parent_dir" "$base_name"
}

# Garante que um caminho esteja estritamente dentro da raiz do projeto.
is_inside_project_root() {
  local candidate_path="$1"
  case "$candidate_path" in
    "$PROJECT_ROOT"/*) return 0 ;;
    *) return 1 ;;
  esac
}

# Bloqueia remoção de caminhos protegidos e seus descendentes.
is_protected_path() {
  local candidate_path="$1"
  local protected_relative_path
  local protected_absolute_path

  for protected_relative_path in "${PROTECTED_RELATIVE_PATHS[@]}"; do
    protected_absolute_path="$PROJECT_ROOT/$protected_relative_path"
    if [ "$candidate_path" = "$protected_absolute_path" ]; then
      return 0
    fi
    case "$candidate_path" in
      "$protected_absolute_path"/*) return 0 ;;
    esac
  done
  return 1
}

# Cria um registro temporário de candidatos e agenda limpeza automática.
initialize_candidate_registry() {
  CANDIDATE_REGISTRY_FILE="$(mktemp "${TMPDIR:-/tmp}/project-cleanup-candidates.XXXXXX")"
  trap 'rm -f "$CANDIDATE_REGISTRY_FILE"' EXIT
}

# Monta expressão `find ... -prune` para ignorar diretórios protegidos.
build_protected_find_prune_args() {
  local protected_relative_path
  PROTECTED_FIND_PRUNE_ARGS=()
  for protected_relative_path in "${PROTECTED_RELATIVE_PATHS[@]}"; do
    PROTECTED_FIND_PRUNE_ARGS+=(-path "$PROJECT_ROOT/$protected_relative_path" -o)
  done
  unset "PROTECTED_FIND_PRUNE_ARGS[$((${#PROTECTED_FIND_PRUNE_ARGS[@]} - 1))]"
}

# Adiciona um candidato somente se passar por todas as validações de segurança.
add_candidate() {
  local raw_path="$1"
  local resolved_path

  # Ignora caminhos inexistentes/sumidos.
  if [ ! -e "$raw_path" ] && [ ! -L "$raw_path" ]; then
    return 0
  fi

  # Normaliza caminho para validação confiável.
  resolved_path="$(resolve_existing_path "$raw_path")" || return 0
  if ! is_inside_project_root "$resolved_path"; then
    return 0
  fi
  if is_protected_path "$resolved_path"; then
    return 0
  fi
  printf '%s\n' "$resolved_path" >>"$CANDIDATE_REGISTRY_FILE"
}

# Coleta diretórios de artefato apenas na raiz do projeto.
collect_root_level_directories() {
  local directory_name
  local absolute_directory_path

  for directory_name in "${ROOT_LEVEL_DIRECTORIES[@]}"; do
    absolute_directory_path="$PROJECT_ROOT/$directory_name"
    if [ -d "$absolute_directory_path" ]; then
      add_candidate "$absolute_directory_path"
    fi
  done
  return 0
}

# Aplica múltiplos padrões em uma única chamada de `find` para reduzir forks.
collect_patterns() {
  local entry_type="$1"
  shift
  local match_path
  local name_expression=()
  local pattern
  local is_first_pattern=1

  # Sai cedo quando nao ha padroes para buscar.
  if [ $# -eq 0 ]; then
    return 0
  fi

  # Monta expressao agrupada `\( -name p1 -o -name p2 ... \)` para varrer tudo de uma vez.
  name_expression+=(\()
  for pattern in "$@"; do
    if [ "$is_first_pattern" -eq 1 ]; then
      is_first_pattern=0
    else
      name_expression+=(-o)
    fi
    name_expression+=(-name "$pattern")
  done
  name_expression+=(\))

  # Usa separador nulo para suportar espaços/caracteres especiais.
  while IFS= read -r -d '' match_path; do
    add_candidate "$match_path"
  done < <(
    find "$PROJECT_ROOT" \
      \( "${PROTECTED_FIND_PRUNE_ARGS[@]}" \) -prune \
      -o -type "$entry_type" "${name_expression[@]}" -print0
  )
}

# Ordena/remove duplicados e carrega os candidatos em memória.
load_candidates() {
  local candidate_path
  sort -u "$CANDIDATE_REGISTRY_FILE" -o "$CANDIDATE_REGISTRY_FILE"
  DELETION_CANDIDATES=()
  while IFS= read -r candidate_path; do
    if [ -n "$candidate_path" ]; then
      DELETION_CANDIDATES+=("$candidate_path")
    fi
  done <"$CANDIDATE_REGISTRY_FILE"
  return 0
}

# Verifica se um item já está coberto por um diretório pai da lista final.
candidate_has_compacted_parent_directory() {
  local candidate_path="$1"
  local compacted_path

  # Sintaxe compatível com bash antigo + `set -u` quando array está vazio.
  for compacted_path in "${COMPACTED_CANDIDATES[@]+"${COMPACTED_CANDIDATES[@]}"}"; do
    if [ -d "$compacted_path" ]; then
      case "$candidate_path" in
        "$compacted_path"/*) return 0 ;;
      esac
    fi
  done
  return 1
}

# Remove itens redundantes da listagem (filhos de diretórios já marcados).
compact_candidates() {
  local candidate_path

  COMPACTED_CANDIDATES=()
  # Sintaxe compatível com bash antigo + `set -u` quando array está vazio.
  for candidate_path in "${DELETION_CANDIDATES[@]+"${DELETION_CANDIDATES[@]}"}"; do
    if candidate_has_compacted_parent_directory "$candidate_path"; then
      continue
    fi
    COMPACTED_CANDIDATES+=("$candidate_path")
  done
  DELETION_CANDIDATES=("${COMPACTED_CANDIDATES[@]+"${COMPACTED_CANDIDATES[@]}"}")
}

# Converte caminho absoluto para relativo, melhorando a leitura da saída.
to_relative_path() {
  local absolute_path="$1"
  printf '%s\n' "${absolute_path#"$PROJECT_ROOT"/}"
}

# Mostra prévia numerada dos itens que podem ser removidos.
print_candidates() {
  local index=1
  local candidate_path
  local item_type

  echo "Itens marcados para limpeza:"
  for candidate_path in "${DELETION_CANDIDATES[@]}"; do
    item_type="ARQ"
    [ -d "$candidate_path" ] && item_type="DIR"
    printf '  %3d. [%s] %s\n' "$index" "$item_type" "$(to_relative_path "$candidate_path")"
    index=$((index + 1))
  done
}

# Exige confirmação textual exata antes de qualquer remoção.
confirm_cleanup() {
  local confirmation_phrase
  local typed_confirmation
  confirmation_phrase="APAGAR ${#DELETION_CANDIDATES[@]} ITENS"

  # Evita confirmação via pipe/script para reduzir risco de execução acidental.
  if [ ! -t 0 ]; then
    echo "Erro: confirmacao exige terminal interativo."
    exit 1
  fi

  echo
  echo "Para executar a limpeza, digite exatamente:"
  echo "  $confirmation_phrase"
  read -r -p "> " typed_confirmation

  if [ "$typed_confirmation" != "$confirmation_phrase" ]; then
    echo
    echo "Limpeza cancelada. Nenhum item foi apagado."
    exit 0
  fi
}

# Remove um candidato individual mantendo as mesmas checagens de segurança.
remove_candidate_safely() {
  local candidate_path="$1"
  local resolved_path

  # Item já removido por outro passo não é tratado como erro.
  if [ ! -e "$candidate_path" ] && [ ! -L "$candidate_path" ]; then
    return 0
  fi

  # Revalida limites e proteção antes de apagar.
  resolved_path="$(resolve_existing_path "$candidate_path")" || return 0
  if ! is_inside_project_root "$resolved_path"; then
    echo "[ignorado] fora da raiz: $resolved_path"
    return 0
  fi
  if is_protected_path "$resolved_path"; then
    echo "[ignorado] protegido: $(to_relative_path "$resolved_path")"
    return 0
  fi

  if [ -d "$resolved_path" ]; then
    rm -rf -- "$resolved_path"
  else
    rm -f -- "$resolved_path"
  fi
  echo "[apagado] $(to_relative_path "$resolved_path")"
}

# Executa remoção em lote usando o mesmo fluxo seguro por item.
execute_cleanup() {
  local candidate_path
  for candidate_path in "${DELETION_CANDIDATES[@]}"; do
    remove_candidate_safely "$candidate_path"
  done
}

# Exibe um cabeçalho visual com os dados principais da execução.
print_execution_header() {
  local border="============================================================"

  echo "
  
  
  "
  echo "                     LIMPEZA DO PROJETO"
  echo "$border"
  echo "Projeto alvo : $PROJECT_ROOT"
  echo "Protegidos   : ${PROTECTED_RELATIVE_PATHS[*]}"
  echo "$border"
  echo
}

# Orquestra todo o fluxo: validar entrada, coletar, revisar, confirmar e limpar.
main() {
  # Exibe ajuda sem executar coleta/remoção.
  if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    print_usage
    exit 0
  fi

  # Bloqueia qualquer argumento para impedir limpeza de outros projetos.
  if [ $# -ne 0 ]; then
    echo "Erro: este script limpa apenas o projeto onde ele esta salvo."
    print_usage
    exit 1
  fi

  print_execution_header

  # Etapa de descoberta dos itens candidatos.
  initialize_candidate_registry
  build_protected_find_prune_args
  collect_root_level_directories
  collect_patterns d "${GLOBAL_DIRECTORY_PATTERNS[@]}"
  collect_patterns f "${GLOBAL_FILE_PATTERNS[@]}"
  load_candidates
  compact_candidates

  # Sai cedo quando não há artefatos para remover.
  if [ "${#DELETION_CANDIDATES[@]}" -eq 0 ]; then
    echo "Nenhum item para limpar."
    exit 0
  fi

  # Etapa de revisão humana e confirmação explícita.
  print_candidates
  confirm_cleanup

  echo
  echo "Executando limpeza..."
  # Etapa final: remoção efetiva.
  execute_cleanup
  echo
  echo "Limpeza concluida com seguranca."
}

# Ponto de entrada do script.
main "$@"
