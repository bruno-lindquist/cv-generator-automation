"""Localization and text formatting helpers."""

from __future__ import annotations

import re
from typing import Any
from xml.sax.saxutils import escape

MONTHS_BY_LANGUAGE = {
    "pt": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}

TAG_MARKERS = {
    "<b>": "___BOLD_START___",
    "</b>": "___BOLD_END___",
    "<i>": "___ITALIC_START___",
    "</i>": "___ITALIC_END___",
    "<u>": "___UNDERLINE_START___",
    "</u>": "___UNDERLINE_END___",
}

FILENAME_SANITIZATION_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def get_translation(
    translations: dict[str, Any],
    language: str,
    section: str,
    key: str,
    default: str,
) -> str:
    """Read a translated string with safe fallback."""
    language_scope = translations.get(language)
    if isinstance(language_scope, dict):
        return language_scope.get(section, {}).get(key, default)

    return translations.get(section, {}).get(key, default)


def get_localized_field(data: Any, field_name: str, language: str, default: str = "") -> str:
    """Resolve localized fields with Portuguese and base-field fallback."""
    if not isinstance(data, dict):
        return default

    localized_value = data.get(f"{field_name}_{language}")
    portuguese_fallback = data.get(f"{field_name}_pt") if language != "pt" else None
    neutral_fallback = data.get(field_name)

    resolved_value = localized_value or portuguese_fallback or neutral_fallback or ""
    if isinstance(resolved_value, str):
        return resolved_value.strip() or default
    return str(resolved_value).strip() or default


def escape_text_preserving_tags(raw_text: Any) -> str:
    """Escape XML entities while preserving supported formatting tags."""
    text = str(raw_text)

    protected_text = text
    for tag, marker in TAG_MARKERS.items():
        protected_text = protected_text.replace(tag, marker)

    escaped_text = escape(protected_text, {"'": "&apos;", '"': "&quot;"})

    for tag, marker in TAG_MARKERS.items():
        escaped_text = escaped_text.replace(marker, tag)

    return escaped_text


def process_rich_text(raw_text: Any) -> str:
    """Escape text and map line breaks to ReportLab line breaks."""
    return escape_text_preserving_tags(raw_text).replace("\n", "<br/>")


def format_month(raw_month: Any, language: str) -> str:
    """Convert numeric month into locale-aware abbreviation."""
    try:
        month_number = int(raw_month)
    except (TypeError, ValueError):
        return str(raw_month)

    if not 1 <= month_number <= 12:
        return str(raw_month)

    months = MONTHS_BY_LANGUAGE.get(language, MONTHS_BY_LANGUAGE["pt"])
    return months[month_number - 1]


def format_period(
    *,
    start_month: Any,
    start_year: Any,
    end_month: Any,
    end_year: Any,
    translations: dict[str, Any],
    language: str,
) -> str:
    """Format a work/education period using locale-aware labels."""
    initial_month = format_month(start_month, language)
    start_period = f"{initial_month} {start_year}".strip()

    if end_month and end_year:
        final_month = format_month(end_month, language)
        return f"{start_period} - {final_month} {end_year}".strip()

    current_label = get_translation(translations, language, "labels", "current", "Present")
    return f"{start_period} - {current_label}".strip()


def sanitize_filename_component(raw_value: Any, fallback: str = "CV") -> str:
    """Return a safe filename component without path separators or unsafe characters."""
    escaped_value = FILENAME_SANITIZATION_PATTERN.sub("_", str(raw_value).strip())
    normalized_value = escaped_value.strip("._-")
    return normalized_value or fallback
