# Formatadores de secoes diretas (premios, idiomas, habilidades) com composicao enxuta.
from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base import BaseSectionFormatter


# Renderiza itens de premios no formato titulo + descricao.
class AwardsSectionFormatter(BaseSectionFormatter):

    # Converte um premio em linha composta para o corpo da secao.
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


# Renderiza idiomas com nivel de proficiencia em formato compacto.
class LanguagesSectionFormatter(BaseSectionFormatter):

    # Monta linha de idioma combinando nome e proficiencia localizada.
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


# Renderiza certificacoes preservando contexto de emissor e ano quando disponivel.
class CertificationsSectionFormatter(BaseSectionFormatter):

    # Compoe texto de certificacao evitando exibir ano isolado sem nome do certificado.
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
        # Ano só aparece quando existe nome da certificação para evitar rótulo órfão.
        if certification_name and issuer_name and year:
            detail_text = f"{issuer_name} ({year})"

        self.add_composite_body_paragraph(
            elements,
            styles,
            main_text=certification_name,
            detail_text=detail_text,
        )


# Renderiza grupos de habilidades em formato categoria + lista separada por virgulas.
class SkillsSectionFormatter(BaseSectionFormatter):

    # Adiciona titulo da categoria e lista de habilidades mantendo espacamento padrao.
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


# Renderiza habilidades centrais como bullets por categoria.
class CoreSkillsSectionFormatter(BaseSectionFormatter):

    # Adiciona categoria e descricoes em bullet com espacamento minimo entre itens.
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
