# Verifica mapeamento entre tipo de secao e formatador retornado pelo registro.
from __future__ import annotations

from tests.helpers.style_helpers import load_project_style_configuration

from infrastructure.pdf_sections import (
    ExperienceSectionFormatter,
    build_default_section_formatter_registry,
)
from infrastructure.pdf_styles import PdfStyleEngine


# Garante o comportamento "registry returns formatter for known section type" para evitar regressao dessa regra.
def test_registry_returns_formatter_for_known_section_type() -> None:
    style_engine = PdfStyleEngine(load_project_style_configuration())
    registry = build_default_section_formatter_registry(
        language="pt",
        translations={},
        pdf_style_engine=style_engine,
    )

    formatter = registry.get_formatter("experience")

    assert isinstance(formatter, ExperienceSectionFormatter)


# Garante o comportamento "registry returns none for unknown section type" para evitar regressao dessa regra.
def test_registry_returns_none_for_unknown_section_type() -> None:
    style_engine = PdfStyleEngine(load_project_style_configuration())
    registry = build_default_section_formatter_registry(
        language="pt",
        translations={},
        pdf_style_engine=style_engine,
    )

    formatter = registry.get_formatter("unknown_section")

    assert formatter is None
