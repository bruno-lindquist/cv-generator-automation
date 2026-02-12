"""Shared validation helpers for style configuration modules."""

from __future__ import annotations

from typing import Any

from shared.exceptions import PdfRenderError


def require_dictionary_section(
    style_configuration: dict[str, Any],
    section_key: str,
    error_message: str,
) -> dict[str, Any]:
    """Return a required dictionary section or raise a style error."""
    section_data = style_configuration.get(section_key)
    if not isinstance(section_data, dict):
        raise PdfRenderError(error_message)
    return section_data
