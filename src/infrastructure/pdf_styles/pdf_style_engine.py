"""Semantic style engine used by the PDF renderer."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_styles.paragraph_style_factory import build_pdf_stylesheet
from infrastructure.pdf_styles.style_config_validator import (
    validate_pdf_style_configuration,
)
from infrastructure.pdf_styles.style_values_resolver import (
    resolve_margin_value,
    resolve_social_link_color,
    resolve_spacing_value,
)


class PdfStyleEngine:
    """Provide semantic access to validated PDF style configuration."""

    def __init__(self, style_configuration: dict[str, Any]) -> None:
        self.style_configuration = style_configuration if isinstance(style_configuration, dict) else {}
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
