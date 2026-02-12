from __future__ import annotations

from pathlib import Path
from typing import Any

from tests.helpers.file_helpers import write_json, write_project_styles


def build_default_app_config() -> dict[str, Any]:
    return {
        "files": {
            "data": "../data/cv_data.json",
            "styles": "styles.json",
            "translations": "translations.json",
            "output_dir": "../output",
        },
        "defaults": {
            "language": "pt",
            "encoding": "utf-8",
        },
        "logging": {
            "enabled": True,
            "level": "INFO",
            "directory": "../logs",
        },
    }


def create_test_project_files(
    base_directory: Path,
    *,
    cv_data: dict[str, Any],
    translations: dict[str, Any],
) -> Path:
    config_directory = base_directory / "config"
    data_directory = base_directory / "data"
    config_directory.mkdir(exist_ok=True)
    data_directory.mkdir(exist_ok=True)

    config_path = config_directory / "config.json"
    data_path = data_directory / "cv_data.json"
    styles_path = config_directory / "styles.json"
    translations_path = config_directory / "translations.json"

    write_json(config_path, build_default_app_config())
    write_json(data_path, cv_data)
    write_project_styles(styles_path)
    write_json(translations_path, translations)

    return config_path
