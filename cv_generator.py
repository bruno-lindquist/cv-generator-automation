#!/usr/bin/env python3
# Este arquivo existe para manter compatibilidade com a forma antiga de execução.
# Ele serve como uma "ponte" para o CLI principal que fica dentro de `src/`.
# Organização:
# - calcula caminhos do projeto
# - garante que `src/` esteja no `sys.path`
# - importa e executa a função `main` do CLI
# Entradas esperadas:
# - argumentos de linha de comando (via `sys.argv`, consumidos pelo CLI)

from __future__ import annotations

import sys
from pathlib import Path

# Caminho absoluto da raiz do projeto (pasta onde este arquivo está).
PROJECT_ROOT = Path(__file__).resolve().parent
# Caminho da pasta que contém o código principal da aplicação.
SOURCE_DIRECTORY = PROJECT_ROOT / "src"

# Adiciona `src/` no início do `sys.path` para que `from cli import main` funcione.
# `sys.path` é a lista de pastas onde o Python procura módulos para importar.
if str(SOURCE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIRECTORY))

from cli import main


# Executa o CLI somente quando este arquivo é chamado diretamente.
# `SystemExit` encerra o processo com o código retornado por `main()`.
if __name__ == "__main__":
    raise SystemExit(main())
