"""Resolvers for scalar visual values used by PDF renderer."""

from __future__ import annotations

from typing import Any

from shared.exceptions import PdfRenderError


def resolve_margin_value(style_configuration: dict[str, Any], margin_key: str) -> float:
    """Resolve and convert a required margin key to float."""
    margins_section = _require_dictionary(
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


def resolve_spacing_value(style_configuration: dict[str, Any], spacing_key: str) -> float:
    """Resolve and convert a required spacing key to float."""
    spacing_section = _require_dictionary(
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
    """Resolve social link color from style configuration."""
    links_section = _require_dictionary(
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


def _require_dictionary(
    style_configuration: dict[str, Any],
    section_key: str,
    error_message: str,
) -> dict[str, Any]:
    section_data = style_configuration.get(section_key)
    if not isinstance(section_data, dict):
        raise PdfRenderError(error_message)
    return section_data
