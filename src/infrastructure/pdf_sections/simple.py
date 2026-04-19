# Formatadores de secoes diretas (premios, idiomas, habilidades) com composicao enxuta.
from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base import BaseSectionFormatter


# Renderiza itens de premios no formato titulo + descricao.
class AwardsSectionFormatter(BaseSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        self.add_composite_body_paragraph(
            elements,
            styles,
            main_text=self.localized_field(section_item, "title"),
            detail_text=self.localized_field(section_item, "description"),
        )


# Renderiza idiomas com nivel de proficiencia em formato compacto.
class LanguagesSectionFormatter(BaseSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        self.add_composite_body_paragraph(
            elements,
            styles,
            main_text=self.localized_field(section_item, "language"),
            detail_text=self.localized_field(section_item, "proficiency"),
        )


# Renderiza certificacoes preservando contexto de emissor e ano quando disponivel.
class CertificationsSectionFormatter(BaseSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        name = self.localized_field(section_item, "name")
        issuer = self.localized_field(section_item, "issuer")
        year = str(section_item.get("year", "")).strip()

        # Ano só aparece quando existem nome e emissor para evitar rótulo órfão.
        detail = f"{issuer} ({year})" if name and issuer and year else issuer

        self.add_composite_body_paragraph(elements, styles, main_text=name, detail_text=detail)


# Renderiza grupos de habilidades em formato categoria + lista separada por virgulas.
class SkillsSectionFormatter(BaseSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        self.add_category_title(elements, styles, section_item)
        skills = section_item.get("item", [])
        if isinstance(skills, list):
            self.add_comma_separated_values(elements, styles, skills)
        self.add_spacing(elements, "item_bottom")


# Renderiza habilidades centrais como bullets por categoria.
class CoreSkillsSectionFormatter(BaseSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        self.add_category_title(elements, styles, section_item)
        self.add_bullet_descriptions(
            elements, styles, self.localized_list(section_item, "description")
        )
        self.add_spacing(elements, "minimal_bottom")
