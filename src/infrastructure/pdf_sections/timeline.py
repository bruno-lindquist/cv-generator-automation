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
        # Ordem dos appends mantém leitura visual consistente no PDF.
        title = self.localized_field(section_item, title_field)
        subtitle = self.localized_field(section_item, subtitle_field)
        period = build_period_text(section_item, self.translations, self.language)

        self.add_bold_paragraph(elements, styles, title, "ItemTitleStyle")
        self.add_bold_paragraph(elements, styles, subtitle, "ItemSubtitleStyle")
        self.add_italic_paragraph(elements, styles, period, "DateStyle")
        self.add_bullet_descriptions(
            elements, styles, self.localized_list(section_item, "description")
        )
        self.add_spacing(elements, "small_bottom")


# Especializa timeline para experiencia profissional.
class ExperienceSectionFormatter(TimelineSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        self.format_timeline_item(
            elements, styles, section_item, title_field="position", subtitle_field="company"
        )


# Especializa timeline para formacao academica.
class EducationSectionFormatter(TimelineSectionFormatter):
    def format_section_item(
        self, elements: list[Any], styles: StyleSheet1, section_item: dict[str, Any]
    ) -> None:
        self.format_timeline_item(
            elements, styles, section_item, title_field="degree", subtitle_field="institution"
        )
