from __future__ import annotations

from pathlib import Path

import pytest

from application.cv_service import CvGenerationService
from tests.helpers.file_helpers import write_json


@pytest.fixture()
def isolated_project_files(tmp_path: Path) -> Path:
    config_directory = tmp_path / "config"
    data_directory = tmp_path / "data"
    config_directory.mkdir()
    data_directory.mkdir()

    config_path = config_directory / "config.json"
    data_path = data_directory / "cv_data.json"
    styles_path = config_directory / "styles.json"
    translations_path = config_directory / "translations.json"

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
        data_path,
        {
            "personal_info": {
                "name": "Maria Testadora",
                "email": "maria@example.com",
                "phone": "(11) 99999-0000",
                "location": "São Paulo, SP",
            },
            "desired_role": {
                "desired_role_pt": "Desenvolvedora Frontend",
                "desired_role_en": "Frontend Developer",
            },
            "summary": {
                "description_pt": "<b>Desenvolvedora</b> com foco em qualidade.",
                "description_en": "<b>Developer</b> focused on quality.",
            },
            "sections": [
                {
                    "type": "experience",
                    "enabled": True,
                    "order": 1,
                }
            ],
            "experience": [
                {
                    "position_pt": "Engenheira de Software",
                    "position_en": "Software Engineer",
                    "company_pt": "Empresa Exemplo",
                    "company_en": "Example Company",
                    "start_month": "1",
                    "start_year": "2020",
                    "end_month": "",
                    "end_year": "",
                    "description_pt": [
                        "Implementou pipelines de CI/CD.",
                    ],
                    "description_en": [
                        "Implemented CI/CD pipelines.",
                    ],
                }
            ],
        },
    )

    write_json(
        styles_path,
        {
            "margins": {
                "top": 10,
                "bottom": 8,
                "left": 12,
                "right": 12,
            },
            "spacing": {
                "header_bottom": 0,
                "section_bottom": 2,
                "item_bottom": 1,
                "small_bottom": 1,
                "minimal_bottom": 0.1,
            },
        },
    )

    write_json(
        translations_path,
        {
            "pt": {
                "sections": {
                    "summary": "Resumo",
                    "experience": "Experiência Profissional",
                },
                "labels": {
                    "current": "Atual",
                },
            },
            "en": {
                "sections": {
                    "summary": "Summary",
                    "experience": "Work Experience",
                },
                "labels": {
                    "current": "Present",
                },
            },
        },
    )

    return config_path


@pytest.mark.parametrize(
    ("language", "expected_suffix"),
    [
        ("pt", ".pdf"),
        ("en", "_EN.pdf"),
    ],
)
def test_cv_generation_service_generates_pdf_with_expected_name(
    isolated_project_files: Path,
    language: str,
    expected_suffix: str,
) -> None:
    generation_service = CvGenerationService(config_file_path=isolated_project_files)

    generated_file_path = generation_service.generate(
        language=language,
        input_file_path=None,
        output_file_path=None,
    )

    assert generated_file_path.exists()
    assert generated_file_path.stat().st_size > 1000
    assert generated_file_path.name.endswith(expected_suffix)


def test_cv_generation_service_respects_output_override(
    isolated_project_files: Path,
) -> None:
    generation_service = CvGenerationService(config_file_path=isolated_project_files)
    custom_output_path = isolated_project_files.parent / "output" / "custom_name.pdf"

    generated_file_path = generation_service.generate(
        language="pt",
        input_file_path=None,
        output_file_path=str(custom_output_path),
    )

    assert generated_file_path == custom_output_path.resolve()
    assert generated_file_path.exists()
