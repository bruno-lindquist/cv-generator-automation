"""JSON file repository abstraction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shared.exceptions import JsonFileNotFoundError, JsonParsingError


class JsonRepository:
    """Read JSON documents from disk using a configured encoding."""

    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def load_json(self, file_path: Path) -> dict[str, Any]:
        resolved_path = file_path.expanduser().resolve()

        if not resolved_path.exists():
            raise JsonFileNotFoundError(f"JSON file not found: {resolved_path}")

        try:
            with resolved_path.open("r", encoding=self.encoding) as json_file:
                data = json.load(json_file)
        except json.JSONDecodeError as exc:
            raise JsonParsingError(f"Invalid JSON file: {resolved_path}") from exc

        if not isinstance(data, dict):
            raise JsonParsingError(f"Top-level JSON object must be a dictionary: {resolved_path}")

        return data
