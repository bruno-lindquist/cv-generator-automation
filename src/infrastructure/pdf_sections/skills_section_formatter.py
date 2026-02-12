"""Formatter for the skills section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter


class SkillsSectionFormatter(BaseSectionFormatter):
    """Render one skills group item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        self.add_category_title(elements, styles, section_item)

        skills = section_item.get("item", [])
        if isinstance(skills, list):
            self.add_comma_separated_values(elements, styles, skills)

        self.add_spacing(elements, "item_bottom")
