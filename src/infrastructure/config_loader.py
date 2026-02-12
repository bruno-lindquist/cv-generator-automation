"""Load and validate application configuration from JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from exceptions import ConfigurationError


@dataclass(frozen=True)
class FileSettings:
    data: str
    data_by_language: dict[str, str] | None
    styles: str
    translations: str
    translations_by_language: dict[str, str] | None
    output_dir: str


@dataclass(frozen=True)
class DefaultSettings:
    language: str
    encoding: str


@dataclass(frozen=True)
class LoggingSettings:
    enabled: bool
    level: str
    directory: str


@dataclass(frozen=True)
class AppConfig:
    files: FileSettings
    defaults: DefaultSettings
    logging: LoggingSettings


def load_app_config(config_file_path: Path) -> AppConfig:
    """Load config file and return parsed app configuration."""
    resolved_config_path = config_file_path.expanduser().resolve()

    if not resolved_config_path.exists():
        raise ConfigurationError(f"Configuration file not found: {resolved_config_path}")

    try:
        with resolved_config_path.open("r", encoding="utf-8") as config_file:
            raw_config = json.load(config_file)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(
            f"Configuration file has invalid JSON: {resolved_config_path}"
        ) from exc

    return _parse_config(raw_config)


def _parse_config(raw_config: dict[str, Any]) -> AppConfig:
    files_section = raw_config.get("files")
    defaults_section = raw_config.get("defaults", {})
    logging_section = raw_config.get("logging", {})

    if not isinstance(files_section, dict):
        raise ConfigurationError("Missing required 'files' section in config")

    required_file_keys = ["styles", "output_dir"]
    missing_file_keys = [
        key for key in required_file_keys if not files_section.get(key)
    ]

    has_data_mapping = isinstance(files_section.get("data_by_language"), dict)
    has_translations_mapping = isinstance(
        files_section.get("translations_by_language"),
        dict,
    )

    if not files_section.get("data") and not has_data_mapping:
        missing_file_keys.append("data or data_by_language")
    if not files_section.get("translations") and not has_translations_mapping:
        missing_file_keys.append("translations or translations_by_language")

    if missing_file_keys:
        missing_keys_str = ", ".join(missing_file_keys)
        raise ConfigurationError(
            f"Missing required config keys in 'files': {missing_keys_str}"
        )

    data_by_language = _parse_language_mapping(
        files_section.get("data_by_language"),
        "data_by_language",
    )
    translations_by_language = _parse_language_mapping(
        files_section.get("translations_by_language"),
        "translations_by_language",
    )

    file_settings = FileSettings(
        data=str(files_section.get("data", "")),
        data_by_language=data_by_language,
        styles=str(files_section["styles"]),
        translations=str(files_section.get("translations", "")),
        translations_by_language=translations_by_language,
        output_dir=str(files_section["output_dir"]),
    )

    default_settings = DefaultSettings(
        language=str(defaults_section.get("language", "pt")).lower(),
        encoding=str(defaults_section.get("encoding", "utf-8")),
    )

    logging_settings = LoggingSettings(
        enabled=bool(logging_section.get("enabled", True)),
        level=str(logging_section.get("level", "INFO")).upper(),
        directory=str(logging_section.get("directory", "logs")),
    )

    return AppConfig(
        files=file_settings,
        defaults=default_settings,
        logging=logging_settings,
    )


def _parse_language_mapping(
    raw_mapping: Any,
    mapping_key: str,
) -> dict[str, str] | None:
    if raw_mapping is None:
        return None

    if not isinstance(raw_mapping, dict):
        raise ConfigurationError(f"Key '{mapping_key}' must be a dictionary")

    parsed_mapping: dict[str, str] = {}
    for language_code, file_path in raw_mapping.items():
        if not isinstance(language_code, str):
            raise ConfigurationError(
                f"Key '{mapping_key}' has non-string language code"
            )
        if not isinstance(file_path, str) or not file_path.strip():
            raise ConfigurationError(
                f"Key '{mapping_key}' has invalid path for language '{language_code}'"
            )
        parsed_mapping[language_code.lower()] = file_path

    if not parsed_mapping:
        raise ConfigurationError(f"Key '{mapping_key}' cannot be empty")

    return parsed_mapping
