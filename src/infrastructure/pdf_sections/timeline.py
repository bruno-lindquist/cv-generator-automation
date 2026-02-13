# Formatadores para secoes cronologicas como experiencia e formacao academica.
from __future__ import annotations

from typing import Any

from reportlab.lib.styles import StyleSheet1

from infrastructure.pdf_sections.base import BaseSectionFormatter, build_period_text


# Base para secoes cronologicas com titulo, subtitulo, periodo e bullets.
class TimelineSectionFormatter(BaseSectionFormatter):

    # Renderiza item cronologico respeitando ordem visual e formatacao de datas.
    def format_timeline_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
        *,
        title_field: str,
        subtitle_field: str,
    ) -> None:
        title_text = self.localized_field(section_item, title_field)
        subtitle_text = self.localized_field(section_item, subtitle_field)
        period_text = build_period_text(section_item, self.translations, self.language)

        # A ordem abaixo mantém leitura visual consistente no PDF.
        self.add_bold_paragraph(elements, styles, title_text, "ItemTitleStyle")
        self.add_bold_paragraph(elements, styles, subtitle_text, "ItemSubtitleStyle")
        self.add_italic_paragraph(elements, styles, period_text, "DateStyle")

        descriptions = self.localized_list(section_item, "description")
        self.add_bullet_descriptions(elements, styles, descriptions)
        self.add_spacing(elements, "small_bottom")


# Especializa timeline para experiencia profissional.
class ExperienceSectionFormatter(TimelineSectionFormatter):

    # Mapeia campos de experiencia (cargo/empresa) para o fluxo cronologico comum.
    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        self.format_timeline_item(
            elements,
            styles,
            section_item,
            title_field="position",
            subtitle_field="company",
        )


# Especializa timeline para formacao academica.
class EducationSectionFormatter(TimelineSectionFormatter):

    # Mapeia campos de educacao (curso/instituicao) para o fluxo cronologico comum.
    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        self.format_timeline_item(
            elements,
            styles,
            section_item,
            title_field="degree",
            subtitle_field="institution",
        )
