"""Factory for ReportLab paragraph styles from JSON style configuration."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet

from shared.exceptions import PdfRenderError

from infrastructure.pdf_styles.style_config_validator import validate_pdf_style_configuration

STYLE_FIELD_MAPPING = {
    "font_name": "fontName",
    "font_size": "fontSize",
    "text_color": "textColor",
    "space_before": "spaceBefore",
    "space_after": "spaceAfter",
    "left_indent": "leftIndent",
    "alignment": "alignment",
    "keep_with_next": "keepWithNext",
}
ALIGNMENT_BY_NAME = {
    "left": TA_LEFT,
    "center": TA_CENTER,
    "right": TA_RIGHT,
    "justify": TA_JUSTIFY,
}


def build_pdf_stylesheet(style_configuration: dict[str, Any]) -> StyleSheet1:
    """Build a StyleSheet1 from paragraph style definitions in the config."""
    validate_pdf_style_configuration(style_configuration)
    paragraph_styles = style_configuration["paragraph_styles"]
    stylesheet = getSampleStyleSheet()

    for style_name, style_definition in paragraph_styles.items():
        if not isinstance(style_name, str) or not isinstance(style_definition, dict):
            continue
        if style_name in stylesheet.byName:
            continue

        parent_name = str(style_definition.get("parent", "Normal"))
        parent_style = stylesheet[parent_name] if parent_name in stylesheet.byName else stylesheet["Normal"]
        style_kwargs = _build_paragraph_style_kwargs(style_definition)
        stylesheet.add(ParagraphStyle(name=style_name, parent=parent_style, **style_kwargs))

    return stylesheet


def _build_paragraph_style_kwargs(style_definition: dict[str, Any]) -> dict[str, Any]:
    style_kwargs: dict[str, Any] = {}
    for setting_key, reportlab_key in STYLE_FIELD_MAPPING.items():
        if setting_key not in style_definition:
            continue

        setting_value = style_definition[setting_key]
        if setting_key == "alignment":
            style_kwargs[reportlab_key] = _resolve_alignment(setting_value)
            continue
        if setting_key == "text_color":
            style_kwargs[reportlab_key] = _resolve_color(setting_value)
            continue

        style_kwargs[reportlab_key] = setting_value

    return style_kwargs


def _resolve_alignment(alignment_value: Any) -> int:
    if isinstance(alignment_value, int):
        return alignment_value
    if not isinstance(alignment_value, str):
        return TA_LEFT
    return ALIGNMENT_BY_NAME.get(alignment_value.lower(), TA_LEFT)


def _resolve_color(color_value: Any) -> colors.Color:
    if not isinstance(color_value, str) or not color_value.strip():
        raise PdfRenderError("Paragraph style 'text_color' must be a non-empty string")
    try:
        return colors.toColor(color_value)
    except ValueError as parse_error:
        raise PdfRenderError(f"Invalid paragraph style color: {color_value}") from parse_error
