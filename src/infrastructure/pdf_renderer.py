# Renderizador principal que converte dados do curriculo em um documento PDF com ReportLab.
from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import StyleSheet1
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from exceptions import PdfRenderError
from infrastructure.pdf_sections import (
    build_default_section_formatter_registry,
)
from infrastructure.pdf_styles import (
    PdfStyleEngine,
)
from localization import (
    escape_text_preserving_tags,
    escape_xml_attribute,
    get_localized_field,
    get_translation,
    process_rich_text,
)


# Renderizador do documento que combina estilos, traducoes e formatadores de secao.
class CvPdfRenderer:
    # Ordem padrao quando o JSON nao especifica a ordem das secoes.
    DEFAULT_SECTION_ORDER = [
        "experience",
        "education",
        "core_skills",
        "skills",
        "languages",
        "awards",
        "certifications",
    ]

    def __init__(
        self,
        *,
        language: str,
        translations: dict[str, Any],
        visual_settings: dict[str, Any],
    ) -> None:
        self.language = language
        self.translations = translations
        self.pdf_style_engine = PdfStyleEngine(visual_settings)
        self.section_formatter_registry = build_default_section_formatter_registry(
            language=language,
            translations=translations,
            pdf_style_engine=self.pdf_style_engine,
        )

    def render_cv(
        self,
        *,
        cv_data: dict[str, Any],
        output_file_path: Path,
        app_logger: Any,
    ) -> Path:
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        document = SimpleDocTemplate(
            str(output_file_path),
            pagesize=A4,
            rightMargin=self.pdf_style_engine.margin("right") * mm,
            leftMargin=self.pdf_style_engine.margin("left") * mm,
            topMargin=self.pdf_style_engine.margin("top") * mm,
            bottomMargin=self.pdf_style_engine.margin("bottom") * mm,
        )

        elements: list[Any] = []
        styles = self.pdf_style_engine.build_stylesheet()

        self._add_header(elements, styles, cv_data)
        self._add_summary(elements, styles, cv_data)
        self._add_dynamic_sections(elements, styles, cv_data, app_logger)

        try:
            document.build(elements)
        except Exception as exc:  # pragma: no cover - external library behavior
            raise PdfRenderError(f"Failed to build PDF: {output_file_path}") from exc

        app_logger.bind(event="pdf_build_finished", step="pdf_renderer").info(
            "PDF built successfully"
        )
        return output_file_path

    # Helper para o padrao recorrente Paragraph(escape_text_preserving_tags(text), styles[key]).
    @staticmethod
    def _styled_paragraph(text: str, styles: StyleSheet1, style_key: str) -> Paragraph:
        return Paragraph(escape_text_preserving_tags(text), styles[style_key])

    def _add_dynamic_sections(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        cv_data: dict[str, Any],
        app_logger: Any,
    ) -> None:
        for section_type in self._resolve_sections_to_render(cv_data):
            section_items = cv_data.get(section_type, [])
            if not section_items:
                continue

            if not isinstance(section_items, list):
                app_logger.bind(
                    event="section_render_skipped",
                    step=section_type,
                ).warning("Section data is not a list; skipping section")
                continue

            formatter = self.section_formatter_registry.get_formatter(section_type)
            if not formatter:
                app_logger.bind(event="section_render_skipped", step=section_type).warning(
                    "Unknown section type; skipping section"
                )
                continue

            self._add_section_title(elements, styles, section_type)
            for item in section_items:
                formatter.format_section_item(elements, styles, item)
            elements.append(Spacer(1, self.pdf_style_engine.spacing("item_bottom") * mm))

    def _resolve_sections_to_render(self, cv_data: dict[str, Any]) -> list[str]:
        sections_config = cv_data.get("sections")
        if not isinstance(sections_config, list):
            return self.DEFAULT_SECTION_ORDER

        # Mantem apenas secoes habilitadas (enabled=True ou omitido), ordenadas por `order`.
        enabled_sections = sorted(
            (
                section
                for section in sections_config
                if isinstance(section, dict) and section.get("enabled", True)
            ),
            key=lambda section: section.get("order", 999),
        )

        # Filtra duplicatas preservando ordem.
        section_types: list[str] = []
        seen: set[str] = set()
        for section in enabled_sections:
            section_type = section.get("type")
            if isinstance(section_type, str) and section_type and section_type not in seen:
                section_types.append(section_type)
                seen.add(section_type)

        return section_types

    def _add_header(
        self, elements: list[Any], styles: StyleSheet1, cv_data: dict[str, Any]
    ) -> None:
        personal_info = cv_data.get("personal_info", {})

        name = personal_info.get("name", "")
        if name:
            elements.append(self._styled_paragraph(name, styles, "NameStyle"))

        desired_role = get_localized_field(
            cv_data.get("desired_role", {}),
            "desired_role",
            self.language,
            "",
        )
        if desired_role:
            elements.append(self._styled_paragraph(desired_role, styles, "TitleStyle"))

        # Junta contatos em uma linha separada por `|` para leitura compacta.
        phone_number = str(personal_info.get("phone", "")).strip()
        # Regra de negocio: em ingles, numero sem `+55` recebe o prefixo brasileiro.
        if phone_number and self.language == "en" and not phone_number.startswith("+55"):
            phone_number = f"+55 {phone_number}"

        contact_items = [
            value
            for value in (
                phone_number,
                str(personal_info.get("email", "")).strip(),
                str(personal_info.get("location", "")).strip(),
            )
            if value
        ]
        if contact_items:
            elements.append(
                self._styled_paragraph(" | ".join(contact_items), styles, "ContactStyle")
            )

        social_links_paragraph = self._build_social_links_paragraph(personal_info, styles)
        if social_links_paragraph is not None:
            elements.append(social_links_paragraph)

        elements.append(Spacer(1, self.pdf_style_engine.spacing("header_bottom") * mm))

    # Monta paragrafo com links sociais ja escapados, ou retorna None quando nao ha links utilizaveis.
    def _build_social_links_paragraph(
        self,
        personal_info: dict[str, Any],
        styles: StyleSheet1,
    ) -> Paragraph | None:
        social_items = personal_info.get("social") or []
        if not isinstance(social_items, list) or not social_items:
            return None

        # Escapa atributos de cor para nao quebrar a marcacao XML interna do ReportLab.
        escaped_link_color = escape_xml_attribute(self.pdf_style_engine.social_link_color())
        social_links: list[str] = []
        for social_item in social_items:
            if not isinstance(social_item, dict):
                continue
            label = str(social_item.get("label", "")).strip()
            url = str(social_item.get("url", "")).strip()
            if not url:
                continue

            escaped_url = escape_xml_attribute(url)
            escaped_label = escape_text_preserving_tags(label or url)
            social_links.append(
                f'<a href="{escaped_url}" color="{escaped_link_color}">{escaped_label}</a>'
            )

        if not social_links:
            return None
        return Paragraph(" | ".join(social_links), styles["ContactStyle"])

    def _add_summary(
        self, elements: list[Any], styles: StyleSheet1, cv_data: dict[str, Any]
    ) -> None:
        summary = get_localized_field(cv_data.get("summary", {}), "description", self.language, "")
        if not summary:
            return

        section_title = get_translation(
            self.translations,
            self.language,
            "sections",
            "summary",
            "Summary",
        )
        elements.append(self._styled_paragraph(section_title, styles, "SectionTitleStyle"))
        elements.append(Paragraph(process_rich_text(summary), styles["BodyStyle"]))
        elements.append(Spacer(1, self.pdf_style_engine.spacing("section_bottom") * mm))

    def _add_section_title(
        self, elements: list[Any], styles: StyleSheet1, section_type: str
    ) -> None:
        section_title = get_translation(
            self.translations,
            self.language,
            "sections",
            section_type,
            section_type,
        )
        elements.append(self._styled_paragraph(section_title, styles, "SectionTitleStyle"))
