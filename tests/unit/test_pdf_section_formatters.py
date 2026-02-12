from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from reportlab.lib.styles import StyleSheet1
from reportlab.platypus import Paragraph, Spacer

from infrastructure.pdf_sections import (
    AwardsSectionFormatter,
    CertificationsSectionFormatter,
    CoreSkillsSectionFormatter,
    EducationSectionFormatter,
    ExperienceSectionFormatter,
    LanguagesSectionFormatter,
    SkillsSectionFormatter,
)
from infrastructure.pdf_styles import PdfStyleEngine


def _load_project_style_configuration() -> dict[str, Any]:
    styles_file_path = Path(__file__).resolve().parents[2] / "config" / "styles.json"
    return json.loads(styles_file_path.read_text(encoding="utf-8"))


@pytest.fixture()
def formatter_context() -> tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]]:
    style_engine = PdfStyleEngine(_load_project_style_configuration())
    styles = style_engine.build_stylesheet()
    translations = {
        "labels": {
            "current": {
                "pt": "Atual",
                "en": "Present",
            }
        }
    }
    return style_engine, styles, translations


def test_experience_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = ExperienceSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "position": {"pt": "Engenheira de Software"},
            "company": {"pt": "Empresa Exemplo"},
            "start_month": "1",
            "start_year": "2020",
            "description": {"pt": ["Criou pipelines de CI/CD."]},
        },
    )

    assert len(elements) >= 4
    assert isinstance(elements[-1], Spacer)


def test_education_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = EducationSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "degree": {"pt": "Bacharelado em Sistemas"},
            "institution": {"pt": "Universidade Exemplo"},
            "start_month": "2",
            "start_year": "2016",
            "end_month": "12",
            "end_year": "2020",
            "description": {"pt": ["Projeto final em arquitetura de software."]},
        },
    )

    assert len(elements) >= 4
    assert isinstance(elements[-1], Spacer)


def test_core_skills_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = CoreSkillsSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "category": {"pt": "Arquitetura e Backend"},
            "description": {"pt": ["Microsserviços", "Observabilidade"]},
        },
    )

    assert len(elements) >= 3
    assert isinstance(elements[-1], Spacer)


def test_skills_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = SkillsSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "category": {"pt": "Tecnologias"},
            "item": ["Python", "FastAPI", "PostgreSQL"],
        },
    )

    assert len(elements) >= 3
    assert isinstance(elements[-1], Spacer)


def test_languages_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = LanguagesSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "language": {"pt": "Inglês"},
            "proficiency": {"pt": "Avançado"},
        },
    )

    assert len(elements) == 1
    assert isinstance(elements[0], Paragraph)


def test_awards_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = AwardsSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "title": {"pt": "Melhor Projeto"},
            "description": {"pt": "Premiação interna de inovação"},
        },
    )

    assert len(elements) == 1
    assert isinstance(elements[0], Paragraph)


def test_certifications_section_formatter_renders_item(
    formatter_context: tuple[PdfStyleEngine, StyleSheet1, dict[str, Any]],
) -> None:
    style_engine, styles, translations = formatter_context
    formatter = CertificationsSectionFormatter(
        language="pt",
        translations=translations,
        pdf_style_engine=style_engine,
    )
    elements: list[Any] = []

    formatter.format_section_item(
        elements,
        styles,
        {
            "name": {"pt": "AWS Certified Developer"},
            "issuer": {"pt": "Amazon"},
            "year": "2024",
        },
    )

    assert len(elements) == 1
    assert isinstance(elements[0], Paragraph)
