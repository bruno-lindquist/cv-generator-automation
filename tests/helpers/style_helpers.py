# Le configuracao real de estilos para manter testes alinhados com comportamento de producao.
from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

# Centraliza caminho de configuracao para evitar recomputacao em multiplos helpers.
PROJECT_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"
PROJECT_STYLES_PATH = PROJECT_CONFIG_DIR / "styles.json"


# Carrega estilos reais do projeto para validar comportamento sem mocks artificiais.
@functools.cache
def load_project_style_configuration() -> dict[str, Any]:
    return json.loads(PROJECT_STYLES_PATH.read_text(encoding="utf-8"))
