"""Shared formatter behavior for timeline-like sections."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter
from infrastructure.pdf_sections.section_formatting_utils import build_period_text


class TimelineSectionFormatter(BaseSectionFormatter):
    """Reusable rendering flow for sections with title/subtitle/date/bullets."""

    def format_timeline_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
        *,
        title_field: str,
        subtitle_field: str,
    ) -> None:
        title_text = self.localized_field(section_item, title_field)
        subtitle_text = self.localized_field(section_item, subtitle_field)
        period_text = build_period_text(section_item, self.translations, self.language)

        self.add_bold_paragraph(elements, styles, title_text, "ItemTitleStyle")
        self.add_bold_paragraph(elements, styles, subtitle_text, "ItemSubtitleStyle")
        self.add_italic_paragraph(elements, styles, period_text, "DateStyle")

        descriptions = self.localized_list(section_item, "description")
        self.add_bullet_descriptions(elements, styles, descriptions)
        self.add_spacing(elements, "small_bottom")
