"""Style engine components for PDF rendering."""

from infrastructure.pdf_styles.pdf_style_engine import PdfStyleEngine
from infrastructure.pdf_styles.paragraph_style_factory import build_pdf_stylesheet
from infrastructure.pdf_styles.style_config_validator import (
    REQUIRED_PARAGRAPH_STYLE_NAMES,
    validate_pdf_style_configuration,
)
from infrastructure.pdf_styles.style_values_resolver import (
    resolve_margin_value,
    resolve_social_link_color,
    resolve_spacing_value,
)

__all__ = [
    "REQUIRED_PARAGRAPH_STYLE_NAMES",
    "PdfStyleEngine",
    "build_pdf_stylesheet",
    "resolve_margin_value",
    "resolve_social_link_color",
    "resolve_spacing_value",
    "validate_pdf_style_configuration",
]
