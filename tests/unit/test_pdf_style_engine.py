# Garante validacao e resolucao correta das configuracoes de estilo do PDF.
from __future__ import annotations

from copy import deepcopy

import pytest
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from tests.helpers.style_helpers import load_project_style_configuration

from exceptions import PdfRenderError
from infrastructure.pdf_styles import PdfStyleEngine


# Garante o comportamento "pdf style engine rejects missing required style" para evitar regressao dessa regra.
def test_pdf_style_engine_rejects_missing_required_style() -> None:
    style_configuration = load_project_style_configuration()
    # Deep copy evita contaminar o fixture base entre testes.
    mutable_style_configuration = deepcopy(style_configuration)
    paragraph_styles = mutable_style_configuration["paragraph_styles"]
    paragraph_styles.pop("NameStyle", None)

    with pytest.raises(PdfRenderError) as raised_error:
        PdfStyleEngine(mutable_style_configuration)

    assert "Style configuration missing required paragraph styles: NameStyle" in str(
        raised_error.value
    )


# Garante o comportamento "pdf style engine build stylesheet converts alignment and color" para evitar regressao dessa regra.
def test_pdf_style_engine_build_stylesheet_converts_alignment_and_color() -> None:
    style_configuration = load_project_style_configuration()
    mutable_style_configuration = deepcopy(style_configuration)

    body_style = mutable_style_configuration["paragraph_styles"]["BodyStyle"]
    body_style["alignment"] = "right"
    body_style["text_color"] = "#123456"

    stylesheet = PdfStyleEngine(mutable_style_configuration).build_stylesheet()
    rendered_body_style = stylesheet["BodyStyle"]

    assert rendered_body_style.alignment == TA_RIGHT
    assert rendered_body_style.textColor == colors.toColor("#123456")


# Garante o comportamento "pdf style engine exposes semantic style access" para evitar regressao dessa regra.
def test_pdf_style_engine_exposes_semantic_style_access() -> None:
    style_configuration = load_project_style_configuration()

    style_engine = PdfStyleEngine(style_configuration)

    assert style_engine.margin("left") == 12.0
    assert style_engine.spacing("section_bottom") == 2.0
    assert style_engine.social_link_color() == "#1f4e79"


# Garante o comportamento "pdf style engine build stylesheet returns expected style" para evitar regressao dessa regra.
def test_pdf_style_engine_build_stylesheet_returns_expected_style() -> None:
    style_configuration = load_project_style_configuration()

    style_engine = PdfStyleEngine(style_configuration)
    stylesheet = style_engine.build_stylesheet()

    assert "NameStyle" in stylesheet.byName


# Garante o comportamento "pdf style engine rejects missing social link color" para evitar regressao dessa regra.
def test_pdf_style_engine_rejects_missing_social_link_color() -> None:
    style_configuration = load_project_style_configuration()
    mutable_style_configuration = deepcopy(style_configuration)
    mutable_style_configuration["links"].pop("social_link_color", None)

    with pytest.raises(PdfRenderError) as raised_error:
        PdfStyleEngine(mutable_style_configuration)

    assert "Style configuration missing 'links.social_link_color'" in str(raised_error.value)


# Garante o comportamento "pdf style engine constructor validates configuration" para evitar regressao dessa regra.
def test_pdf_style_engine_constructor_validates_configuration() -> None:
    style_configuration = load_project_style_configuration()
    mutable_style_configuration = deepcopy(style_configuration)
    mutable_style_configuration["paragraph_styles"].pop("NameStyle", None)

    with pytest.raises(PdfRenderError) as raised_error:
        PdfStyleEngine(mutable_style_configuration)

    assert "Style configuration missing required paragraph styles: NameStyle" in str(
        raised_error.value
    )
