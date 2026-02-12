"""Simple section formatters with compact rendering rules."""

from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base import BaseSectionFormatter


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


class CoreSkillsSectionFormatter(BaseSectionFormatter):
    """Render one core skills item into reportlab elements."""

    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        self.add_category_title(elements, styles, section_item)

        descriptions = self.localized_list(section_item, "description")
        self.add_bullet_descriptions(elements, styles, descriptions)
        self.add_spacing(elements, "minimal_bottom")
