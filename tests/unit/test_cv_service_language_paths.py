# Valida regras de precedencia e fallback na resolucao de caminhos por idioma.
from __future__ import annotations

from pathlib import Path

import pytest
from tests.helpers.file_helpers import write_json

from cv_service import CvGenerationService
from exceptions import ConfigurationError


# Instancia servico apontando para config temporario para testar apenas resolucao de caminhos.
def _build_generation_service(
    base_directory: Path,
    *,
    files_section: dict,
) -> tuple[CvGenerationService, Path]:
    config_directory = base_directory / "config"
    config_directory.mkdir()
    config_path = config_directory / "config.json"

    write_json(
        config_path,
        {
            "files": files_section,
            "defaults": {"language": "pt", "encoding": "utf-8"},
            "logging": {"enabled": False, "level": "INFO", "directory": "../logs"},
        },
    )
    # Retorna também o diretório base para facilitar assert de caminhos resolvidos.
    return CvGenerationService(config_file_path=config_path), config_directory


# Garante o comportamento "data path prefers direct file when present" para evitar regressao dessa regra.
def test_data_path_prefers_direct_file_when_present(tmp_path: Path) -> None:
    generation_service, config_directory = _build_generation_service(
        tmp_path,
        files_section={
            "data": "../data/default_cv.json",
            "styles": "styles.json",
            "translations": "translations.json",
            "output_dir": "../__output",
        },
    )

    resolved_data_path = generation_service.path_resolver.resolve_language_aware_path(
        direct_path=generation_service.config.files.data,
        path_by_language=generation_service.config.files.data_by_language,
        language="en",
        path_label="data",
    )
    expected_data_path = (config_directory / "../data/default_cv.json").resolve()

    assert resolved_data_path == expected_data_path


# Garante o comportamento "translations path uses mapping when direct path is absent" para evitar regressao dessa regra.
def test_translations_path_uses_mapping_when_direct_path_is_absent(tmp_path: Path) -> None:
    generation_service, config_directory = _build_generation_service(
        tmp_path,
        files_section={
            "data": "../data/default_cv.json",
            "styles": "styles.json",
            "translations": "",
            "translations_by_language": {"en": "../i18n/translations_en.json"},
            "output_dir": "../__output",
        },
    )

    resolved_translations_path = generation_service.path_resolver.resolve_language_aware_path(
        direct_path=generation_service.config.files.translations,
        path_by_language=generation_service.config.files.translations_by_language,
        language="en",
        path_label="translations",
    )
    expected_translations_path = (config_directory / "../i18n/translations_en.json").resolve()

    assert resolved_translations_path == expected_translations_path


# Garante o comportamento "data path raises when language is not configured" para evitar regressao dessa regra.
def test_data_path_raises_when_language_is_not_configured(tmp_path: Path) -> None:
    generation_service, _ = _build_generation_service(
        tmp_path,
        files_section={
            "data": "",
            "data_by_language": {"pt": "../data/cv_pt.json"},
            "styles": "styles.json",
            "translations": "translations.json",
            "output_dir": "../__output",
        },
    )

    with pytest.raises(ConfigurationError) as raised_error:
        generation_service.path_resolver.resolve_language_aware_path(
            direct_path=generation_service.config.files.data,
            path_by_language=generation_service.config.files.data_by_language,
            language="en",
            path_label="data",
        )

    assert "No data file configured for language 'en'" in str(raised_error.value)
