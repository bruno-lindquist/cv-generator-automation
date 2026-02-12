"""Formatter for the education section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter
from infrastructure.pdf_sections.section_formatting_utils import build_period_text


class EducationSectionFormatter(BaseSectionFormatter):
    """Render one education item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        degree = self.localized_field(section_item, "degree")
        institution = self.localized_field(section_item, "institution")
        period_text = build_period_text(section_item, self.translations, self.language)

        self.add_bold_paragraph(elements, styles, degree, "ItemTitleStyle")
        self.add_bold_paragraph(elements, styles, institution, "ItemSubtitleStyle")
        self.add_italic_paragraph(elements, styles, period_text, "DateStyle")

        descriptions = self.localized_list(section_item, "description")
        self.add_bullet_descriptions(elements, styles, descriptions)
        self.add_spacing(elements, "small_bottom")
