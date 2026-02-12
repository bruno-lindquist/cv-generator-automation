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
        category = self.localized_field(section_item, "category")
        if category:
            self.add_plain_paragraph(elements, styles, category, "ItemTitleStyle")

        skills = section_item.get("item", [])
        if isinstance(skills, list) and skills:
            skills_text = ", ".join(str(skill) for skill in skills)
            self.add_plain_paragraph(elements, styles, skills_text, "BodyStyle")

        self.add_spacing(elements, "item_bottom")
