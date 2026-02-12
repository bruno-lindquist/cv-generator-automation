"""Formatter for the languages section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter


class LanguagesSectionFormatter(BaseSectionFormatter):
    """Render one language item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        language_name = self.localized_field(section_item, "language")
        proficiency = self.localized_field(section_item, "proficiency")

        self.add_composite_body_paragraph(
            elements,
            styles,
            main_text=language_name,
            detail_text=proficiency,
        )
