#!/usr/bin/env python3
# Este arquivo existe para manter compatibilidade com a forma antiga de execução.
# Ele serve como uma "ponte" para o CLI principal que fica dentro de `src/`.
# Organização:
# - tenta usar o módulo instalado (`cli`)
# - usa fallback para `src.cli` em execução direta no repositório
# - executa a função `main` do CLI
# Entradas esperadas:
# - argumentos de linha de comando (via `sys.argv`, consumidos pelo CLI)

from __future__ import annotations

try:
    from cli import main
except ModuleNotFoundError:  # pragma: no cover - compatibility fallback
    from src.cli import main


# Executa o CLI somente quando este arquivo é chamado diretamente.
# `SystemExit` encerra o processo com o código retornado por `main()`.
if __name__ == "__main__":
    raise SystemExit(main())
