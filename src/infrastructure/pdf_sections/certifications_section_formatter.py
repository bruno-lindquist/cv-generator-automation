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

        detail_text = issuer_name
        if certification_name and issuer_name and year:
            detail_text = f"{issuer_name} ({year})"

        self.add_composite_body_paragraph(
            elements,
            styles,
            main_text=certification_name,
            detail_text=detail_text,
        )
