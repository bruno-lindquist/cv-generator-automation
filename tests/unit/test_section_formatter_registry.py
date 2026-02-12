from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from infrastructure.pdf_sections import (
    ExperienceSectionFormatter,
    build_default_section_formatter_registry,
)
from infrastructure.pdf_styles import PdfStyleEngine


def _load_project_style_configuration() -> dict[str, Any]:
    styles_file_path = Path(__file__).resolve().parents[2] / "config" / "styles.json"
    return json.loads(styles_file_path.read_text(encoding="utf-8"))


def test_registry_returns_formatter_for_known_section_type() -> None:
    style_engine = PdfStyleEngine(_load_project_style_configuration())
    registry = build_default_section_formatter_registry(
        language="pt",
        translations={},
        pdf_style_engine=style_engine,
    )

    formatter = registry.get_formatter("experience")

    assert isinstance(formatter, ExperienceSectionFormatter)


def test_registry_returns_none_for_unknown_section_type() -> None:
    style_engine = PdfStyleEngine(_load_project_style_configuration())
    registry = build_default_section_formatter_registry(
        language="pt",
        translations={},
        pdf_style_engine=style_engine,
    )

    formatter = registry.get_formatter("unknown_section")

    assert formatter is None
