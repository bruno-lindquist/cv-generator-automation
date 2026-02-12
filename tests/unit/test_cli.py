from __future__ import annotations

from pathlib import Path

from cli import main
from tests.helpers.file_helpers import write_json


def _create_valid_project_files(base_directory: Path) -> Path:
    config_directory = base_directory / "config"
    data_directory = base_directory / "data"
    config_directory.mkdir()
    data_directory.mkdir()

    config_path = config_directory / "config.json"
    write_json(
        config_path,
        {
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
        },
    )
    write_json(
        data_directory / "cv_data.json",
        {
            "personal_info": {"name": "CLI Test", "email": "cli@example.com"},
            "desired_role": {"desired_role_pt": "Desenvolvedor"},
        },
    )
    write_json(config_directory / "styles.json", {"margins": {}, "spacing": {}})
    write_json(
        config_directory / "translations.json",
        {
            "pt": {
                "sections": {"summary": "Resumo"},
                "labels": {"current": "Atual"},
            }
        },
    )
    return config_path


def test_cli_main_returns_zero_for_valid_generation(tmp_path: Path) -> None:
    config_path = _create_valid_project_files(tmp_path)

    exit_code = main(["-c", str(config_path), "-l", "pt"])

    assert exit_code == 0


def test_cli_main_returns_one_for_invalid_config_path() -> None:
    exit_code = main(["-c", "missing-config-file.json"])

    assert exit_code == 1
