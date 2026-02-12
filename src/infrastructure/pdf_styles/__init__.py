"""Style engine components for PDF rendering."""

from infrastructure.pdf_styles.pdf_style_engine import (
    PdfStyleEngine,
    REQUIRED_PARAGRAPH_STYLE_NAMES,
    build_pdf_stylesheet,
    resolve_margin_value,
    resolve_social_link_color,
    resolve_spacing_value,
    validate_pdf_style_configuration,
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
