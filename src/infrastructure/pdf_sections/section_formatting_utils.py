"""Shared helpers used by multiple section formatters."""

from __future__ import annotations

from typing import Any

from domain.localization import format_period


def build_period_text(
    section_item: dict[str, Any],
    translations: dict[str, Any],
    language: str,
) -> str:
    """Build localized start/end period text for timeline-like sections."""
    return format_period(
        start_month=section_item.get("start_month", ""),
        start_year=section_item.get("start_year", ""),
        end_month=section_item.get("end_month", ""),
        end_year=section_item.get("end_year", ""),
        translations=translations,
        language=language,
    )
