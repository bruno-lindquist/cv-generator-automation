"""Formatter for the core skills section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter


class CoreSkillsSectionFormatter(BaseSectionFormatter):
    """Render one core skills item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        category = self.localized_field(section_item, "category")
        if category:
            self.add_plain_paragraph(elements, styles, category, "ItemTitleStyle")

        descriptions = self.localized_list(section_item, "description")
        self.add_bullet_descriptions(elements, styles, descriptions)
        self.add_spacing(elements, "minimal_bottom")
