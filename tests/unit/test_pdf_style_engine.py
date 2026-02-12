from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT

from infrastructure.pdf_styles import PdfStyleEngine
from infrastructure.pdf_styles.paragraph_style_factory import build_pdf_stylesheet
from infrastructure.pdf_styles.style_config_validator import (
    validate_pdf_style_configuration,
)
from shared.exceptions import PdfRenderError


def _load_project_style_configuration() -> dict:
    styles_file_path = Path(__file__).resolve().parents[2] / "config" / "styles.json"
    raw_styles = styles_file_path.read_text(encoding="utf-8")
    return json.loads(raw_styles)


def test_validate_pdf_style_configuration_rejects_missing_required_style() -> None:
    style_configuration = _load_project_style_configuration()
    mutable_style_configuration = deepcopy(style_configuration)
    paragraph_styles = mutable_style_configuration["paragraph_styles"]
    paragraph_styles.pop("NameStyle", None)

    with pytest.raises(PdfRenderError) as raised_error:
        validate_pdf_style_configuration(mutable_style_configuration)

    assert "Style configuration missing required paragraph styles: NameStyle" in str(raised_error.value)


def test_build_pdf_stylesheet_converts_alignment_and_color() -> None:
    style_configuration = _load_project_style_configuration()
    mutable_style_configuration = deepcopy(style_configuration)

    body_style = mutable_style_configuration["paragraph_styles"]["BodyStyle"]
    body_style["alignment"] = "right"
    body_style["text_color"] = "#123456"

    stylesheet = build_pdf_stylesheet(mutable_style_configuration)
    rendered_body_style = stylesheet["BodyStyle"]

    assert rendered_body_style.alignment == TA_RIGHT
    assert rendered_body_style.textColor == colors.toColor("#123456")


def test_pdf_style_engine_exposes_semantic_style_access() -> None:
    style_configuration = _load_project_style_configuration()

    style_engine = PdfStyleEngine(style_configuration)

    assert style_engine.margin("left") == 12.0
    assert style_engine.spacing("section_bottom") == 2.0
    assert style_engine.social_link_color() == "#1f4e79"


def test_pdf_style_engine_build_stylesheet_returns_expected_style() -> None:
    style_configuration = _load_project_style_configuration()

    style_engine = PdfStyleEngine(style_configuration)
    stylesheet = style_engine.build_stylesheet()

    assert "NameStyle" in stylesheet.byName
