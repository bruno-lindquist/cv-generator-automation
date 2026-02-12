"""JSON loading helper with domain-specific error mapping."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from exceptions import JsonFileNotFoundError, JsonParsingError


def load_json(file_path: Path, *, encoding: str = "utf-8") -> dict[str, Any]:
    """Load a JSON file as dictionary with consistent domain errors."""
    resolved_path = file_path.expanduser().resolve()

    if not resolved_path.exists():
        raise JsonFileNotFoundError(f"JSON file not found: {resolved_path}")

    try:
        with resolved_path.open("r", encoding=encoding) as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as exc:
        raise JsonParsingError(f"Invalid JSON file: {resolved_path}") from exc

    if not isinstance(data, dict):
        raise JsonParsingError(
            f"Top-level JSON object must be a dictionary: {resolved_path}"
        )

    return data
