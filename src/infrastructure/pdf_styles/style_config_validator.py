"""Validation helpers for PDF style configuration."""

from __future__ import annotations

from typing import Any

from infrastructure.pdf_styles.style_values_resolver import resolve_social_link_color
from infrastructure.pdf_styles.style_validation_helpers import require_dictionary_section
from shared.exceptions import PdfRenderError

REQUIRED_PARAGRAPH_STYLE_NAMES = [
    "NameStyle",
    "TitleStyle",
    "SectionTitleStyle",
    "ItemTitleStyle",
    "ItemSubtitleStyle",
    "BodyStyle",
    "ContactStyle",
    "DateStyle",
]
REQUIRED_MARGIN_KEYS = [
    "top",
    "bottom",
    "left",
    "right",
]
REQUIRED_SPACING_KEYS = [
    "header_bottom",
    "section_bottom",
    "item_bottom",
    "small_bottom",
    "minimal_bottom",
]


def validate_pdf_style_configuration(style_configuration: dict[str, Any]) -> None:
    """Validate required style configuration blocks and required keys."""
    paragraph_styles = require_dictionary_section(
        style_configuration,
        "paragraph_styles",
        "Style configuration missing 'paragraph_styles' dictionary in styles.json",
    )
    _require_paragraph_style_names(paragraph_styles)
    _require_section_keys(style_configuration, "margins", REQUIRED_MARGIN_KEYS)
    _require_section_keys(style_configuration, "spacing", REQUIRED_SPACING_KEYS)
    resolve_social_link_color(style_configuration)


def _require_paragraph_style_names(paragraph_styles: dict[str, Any]) -> None:
    missing_required_styles = [
        style_name
        for style_name in REQUIRED_PARAGRAPH_STYLE_NAMES
        if style_name not in paragraph_styles
    ]
    if missing_required_styles:
        missing_styles = ", ".join(missing_required_styles)
        raise PdfRenderError(
            f"Style configuration missing required paragraph styles: {missing_styles}"
        )


def _require_section_keys(
    style_configuration: dict[str, Any],
    section_key: str,
    required_keys: list[str],
) -> None:
    section_data = require_dictionary_section(
        style_configuration,
        section_key,
        f"Style configuration missing '{section_key}' dictionary in styles.json",
    )
    for required_key in required_keys:
        if section_data.get(required_key) is None:
            raise PdfRenderError(
                f"Style configuration missing '{section_key}.{required_key}' in styles.json"
            )
