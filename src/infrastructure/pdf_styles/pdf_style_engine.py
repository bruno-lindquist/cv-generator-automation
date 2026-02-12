"""PDF style engine and helpers for validation/value resolution."""

from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet

from exceptions import PdfRenderError

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
REQUIRED_MARGIN_KEYS = ["top", "bottom", "left", "right"]
REQUIRED_SPACING_KEYS = [
    "header_bottom",
    "section_bottom",
    "item_bottom",
    "small_bottom",
    "minimal_bottom",
]


class PdfStyleEngine:
    """Provide semantic access to validated PDF style configuration."""

    def __init__(self, style_configuration: dict[str, Any]) -> None:
        self.style_configuration = (
            style_configuration if isinstance(style_configuration, dict) else {}
        )
        validate_pdf_style_configuration(self.style_configuration)

    def build_stylesheet(self) -> StyleSheet1:
        """Create a ReportLab stylesheet from the style configuration."""
        return build_pdf_stylesheet(self.style_configuration)

    def margin(self, margin_key: str) -> float:
        """Resolve a required margin value."""
        return resolve_margin_value(self.style_configuration, margin_key)

    def spacing(self, spacing_key: str) -> float:
        """Resolve a required spacing value."""
        return resolve_spacing_value(self.style_configuration, spacing_key)

    def social_link_color(self) -> str:
        """Resolve the social link color configured for hyperlinks."""
        return resolve_social_link_color(self.style_configuration)


def validate_pdf_style_configuration(style_configuration: dict[str, Any]) -> None:
    """Validate required style blocks and keys for PDF generation."""
    paragraph_styles = _require_dictionary_section(
        style_configuration,
        "paragraph_styles",
        "Style configuration missing 'paragraph_styles' dictionary in styles.json",
    )
    _require_paragraph_style_names(paragraph_styles)
    _require_required_keys(style_configuration, "margins", REQUIRED_MARGIN_KEYS)
    _require_required_keys(style_configuration, "spacing", REQUIRED_SPACING_KEYS)
    resolve_social_link_color(style_configuration)


def build_pdf_stylesheet(style_configuration: dict[str, Any]) -> StyleSheet1:
    """Build a ReportLab stylesheet from paragraph style definitions."""
    paragraph_styles = style_configuration["paragraph_styles"]
    stylesheet = getSampleStyleSheet()

    for style_name, style_definition in paragraph_styles.items():
        if not isinstance(style_name, str) or not isinstance(style_definition, dict):
            continue
        if style_name in stylesheet.byName:
            continue

        parent_name = str(style_definition.get("parent", "Normal"))
        parent_style = (
            stylesheet[parent_name]
            if parent_name in stylesheet.byName
            else stylesheet["Normal"]
        )
        style_kwargs = _build_paragraph_style_kwargs(style_definition)
        stylesheet.add(
            ParagraphStyle(
                name=style_name,
                parent=parent_style,
                **style_kwargs,
            )
        )

    return stylesheet


def resolve_margin_value(style_configuration: dict[str, Any], margin_key: str) -> float:
    """Resolve a required margin value."""
    margins_section = _require_dictionary_section(
        style_configuration,
        "margins",
        "Style configuration missing 'margins' dictionary in styles.json",
    )
    margin_value = margins_section.get(margin_key)
    if margin_value is None:
        raise PdfRenderError(
            f"Style configuration missing 'margins.{margin_key}' in styles.json"
        )
    return float(margin_value)


def resolve_spacing_value(
    style_configuration: dict[str, Any],
    spacing_key: str,
) -> float:
    """Resolve a required spacing value."""
    spacing_section = _require_dictionary_section(
        style_configuration,
        "spacing",
        "Style configuration missing 'spacing' dictionary in styles.json",
    )
    spacing_value = spacing_section.get(spacing_key)
    if spacing_value is None:
        raise PdfRenderError(
            f"Style configuration missing 'spacing.{spacing_key}' in styles.json"
        )
    return float(spacing_value)


def resolve_social_link_color(style_configuration: dict[str, Any]) -> str:
    """Resolve configured social link color."""
    links_section = _require_dictionary_section(
        style_configuration,
        "links",
        "Style configuration missing 'links' dictionary in styles.json",
    )
    link_color = links_section.get("social_link_color")
    if not isinstance(link_color, str) or not link_color.strip():
        raise PdfRenderError(
            "Style configuration missing 'links.social_link_color' in styles.json"
        )
    return link_color


def _require_dictionary_section(
    style_configuration: dict[str, Any],
    section_key: str,
    error_message: str,
) -> dict[str, Any]:
    section_data = style_configuration.get(section_key)
    if not isinstance(section_data, dict):
        raise PdfRenderError(error_message)
    return section_data


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


def _require_required_keys(
    style_configuration: dict[str, Any],
    section_key: str,
    required_keys: list[str],
) -> None:
    section_data = _require_dictionary_section(
        style_configuration,
        section_key,
        f"Style configuration missing '{section_key}' dictionary in styles.json",
    )
    for required_key in required_keys:
        if section_data.get(required_key) is None:
            raise PdfRenderError(
                f"Style configuration missing '{section_key}.{required_key}' in styles.json"
            )


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
