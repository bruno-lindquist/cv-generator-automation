"""Formatter for the education section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.timeline_section_formatter import TimelineSectionFormatter


class EducationSectionFormatter(TimelineSectionFormatter):
    """Render one education item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        self.format_timeline_item(
            elements,
            styles,
            section_item,
            title_field="degree",
            subtitle_field="institution",
        )
