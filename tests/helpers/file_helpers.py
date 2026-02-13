# Helpers para gravacao de arquivos temporarios usados nos cenarios de teste.
from __future__ import annotations

import json
from pathlib import Path


# Grava JSON de teste com indentacao para facilitar leitura e debug de fixtures.
def write_json(file_path: Path, content: dict) -> None:
    file_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


# Replica o styles.json real no ambiente temporario para aproximar teste de producao.
def write_project_styles(file_path: Path) -> None:
    # Reusa o estilo real do projeto para manter testes alinhados com produção.
    project_styles_path = Path(__file__).resolve().parents[2] / "config" / "styles.json"
    file_path.write_text(project_styles_path.read_text(encoding="utf-8"), encoding="utf-8")
