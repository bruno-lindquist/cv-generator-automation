"""Formatter for the awards section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter


class AwardsSectionFormatter(BaseSectionFormatter):
    """Render one award item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        title = self.localized_field(section_item, "title")
        description = self.localized_field(section_item, "description")

        self.add_composite_body_paragraph(
            elements,
            styles,
            main_text=title,
            detail_text=description,
        )
