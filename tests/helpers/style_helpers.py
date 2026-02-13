# Le configuracao real de estilos para manter testes alinhados com comportamento de producao.
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# Carrega estilos reais do projeto para validar comportamento sem mocks artificiais.
def load_project_style_configuration() -> dict[str, Any]:
    styles_file_path = Path(__file__).resolve().parents[2] / "config" / "styles.json"
    return json.loads(styles_file_path.read_text(encoding="utf-8"))
