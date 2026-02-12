"""Formatter for the certifications section."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter


class CertificationsSectionFormatter(BaseSectionFormatter):
    """Render one certification item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        certification_name = self.localized_field(section_item, "name")
        issuer_name = self.localized_field(section_item, "issuer")
        year = str(section_item.get("year", "")).strip()

        if certification_name and issuer_name:
            detail_text = issuer_name
            if year:
                detail_text = f"{issuer_name} ({year})"
            certification_text = self.compose_bold_with_detail_text(
                certification_name,
                detail_text,
            )
        else:
            certification_text = self.compose_bold_with_detail_text(
                certification_name,
                issuer_name,
            )

        self.add_body_rich_paragraph(elements, styles, certification_text)
