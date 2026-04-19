# Helpers para gravacao de arquivos temporarios usados nos cenarios de teste.
from __future__ import annotations

import json
from pathlib import Path

from tests.helpers.style_helpers import PROJECT_STYLES_PATH


# Grava JSON de teste com indentacao para facilitar leitura e debug de fixtures.
def write_json(file_path: Path, content: dict) -> None:
    file_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


# Replica o styles.json real no ambiente temporario para aproximar teste de producao.
def write_project_styles(file_path: Path) -> None:
    # Reusa o estilo real do projeto para manter testes alinhados com produção.
    file_path.write_text(PROJECT_STYLES_PATH.read_text(encoding="utf-8"), encoding="utf-8")
