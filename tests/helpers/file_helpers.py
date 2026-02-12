from __future__ import annotations

import json
from pathlib import Path


def write_json(file_path: Path, content: dict) -> None:
    file_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
