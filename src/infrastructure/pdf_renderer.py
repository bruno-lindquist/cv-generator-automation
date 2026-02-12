# Este arquivo implementa a camada de renderização de currículo em PDF.
# Ele serve para transformar dados estruturados do CV em elementos visuais (ReportLab).
# Organização:
# - classe `CvPdfRenderer` com fluxo principal de renderização
# - métodos auxiliares para cabeçalho, resumo, seções dinâmicas e títulos
# - resolução da ordem de seções com fallback padrão
# Entradas esperadas:
# - dados do currículo (`cv_data`), traduções, idioma e configurações visuais
# Saídas esperadas:
# - arquivo PDF gravado em disco e retorno do caminho (`Path`)
# - logs de progresso/erros durante a renderização

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import StyleSheet1
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from localization import (
    escape_xml_attribute,
    escape_text_preserving_tags,
    get_localized_field,
    get_translation,
    process_rich_text,
)
from infrastructure.pdf_sections import (
    build_default_section_formatter_registry,
)
from infrastructure.pdf_styles import (
    PdfStyleEngine,
)
from exceptions import PdfRenderError


class CvPdfRenderer:
    # Propósito:
    # - montar um PDF a partir dos dados do CV usando estilos e formatadores de seção.
    # Retorno:
    # - a renderização principal retorna `Path` do PDF gerado.
    # Efeitos:
    # - criação de diretório de saída
    # - escrita de arquivo PDF
    # - emissão de logs do processo

    # Ordem padrão quando o JSON não especifica a ordem das seções.
    # Manter essa lista evita que o PDF fique sem estrutura em casos incompletos.
    DEFAULT_SECTION_ORDER = [
        "experience",
        "education",
        "core_skills",
        "skills",
        "languages",
        "awards",
        "certifications",
    ]

    # Propósito:
    # - inicializar dependências de estilo e registro de formatadores.
    # Efeitos:
    # - instancia `PdfStyleEngine`
    # - monta registry de formatadores com idioma/traduções.
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

    # Propósito:
    # - criar o PDF completo: cabeçalho, resumo e seções.
    # Retorno:
    # - `Path` do arquivo PDF gerado.
    # Efeitos:
    # - cria diretório de saída se necessário
    # - grava o arquivo PDF
    # - registra logs de início/fim e pode lançar `PdfRenderError`.
    def render_cv(
        self,
        *,
        cv_data: dict[str, Any],
        output_file_path: Path,
        app_logger: Any,
    ) -> Path:
        # Garante que a pasta de destino exista antes de tentar gravar o PDF.
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Configura documento base (página A4 e margens convertidas para milímetros).
        document = SimpleDocTemplate(
            str(output_file_path),
            pagesize=A4,
            rightMargin=self.pdf_style_engine.margin("right") * mm,
            leftMargin=self.pdf_style_engine.margin("left") * mm,
            topMargin=self.pdf_style_engine.margin("top") * mm,
            bottomMargin=self.pdf_style_engine.margin("bottom") * mm,
        )

        app_logger.bind(event="pdf_build_started", step="pdf_renderer").info(
            "Building PDF document"
        )

        # `elements` é a sequência de blocos visuais que o ReportLab vai desenhar.
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

    # Propósito:
    # - percorrer seções habilitadas e adicionar itens formatados ao documento.
    # Efeitos:
    # - modifica lista `elements` (estrutura final do PDF)
    # - escreve logs de início/fim de cada seção.
    def _add_dynamic_sections(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        cv_data: dict[str, Any],
        app_logger: Any,
    ) -> None:
        # Define a ordem real (vinda do JSON ou fallback padrão).
        for section_type in self._resolve_sections_to_render(cv_data):
            section_items = cv_data.get(section_type, [])
            if not section_items:
                # Seção vazia: ignora sem erro para manter fluxo resiliente.
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

            # Mede duração de renderização da seção para observabilidade.
            section_start = time.perf_counter()

            self._add_section_title(elements, styles, section_type)
            for item in section_items:
                # Delega a formatação do item para o formatador específico da seção.
                formatter.format_section_item(elements, styles, item)
            elements.append(Spacer(1, self.pdf_style_engine.spacing("item_bottom") * mm))

            elapsed_ms = int((time.perf_counter() - section_start) * 1000)
            app_logger.bind(
                event="section_render_finished",
                step=section_type,
                duration_ms=str(elapsed_ms),
            ).info("Finished section")

    # Propósito:
    # - decidir quais seções serão renderizadas e em qual ordem.
    # Retorno:
    # - lista de nomes de seção (`list[str]`).
    def _resolve_sections_to_render(self, cv_data: dict[str, Any]) -> list[str]:
        sections_config = cv_data.get("sections")
        # Se não houver configuração válida, usa ordem padrão definida na classe.
        if not isinstance(sections_config, list):
            return self.DEFAULT_SECTION_ORDER

        # Mantém apenas seções habilitadas (enabled=True ou omitido).
        enabled_sections = [
            section
            for section in sections_config
            if isinstance(section, dict) and section.get("enabled", True)
        ]
        # Ordena por campo `order` (quanto menor, mais acima no PDF).
        sorted_sections = sorted(enabled_sections, key=lambda section: section.get("order", 999))

        section_types: list[str] = []
        for section in sorted_sections:
            section_type = section.get("type")
            # Evita repetição de seção quando o JSON tiver entradas duplicadas.
            if isinstance(section_type, str) and section_type and section_type not in section_types:
                section_types.append(section_type)

        return section_types

    # Propósito:
    # - montar o cabeçalho do currículo (nome, cargo, contatos e links sociais).
    # Efeitos:
    # - adiciona elementos visuais em `elements`.
    def _add_header(self, elements: list[Any], styles: StyleSheet1, cv_data: dict[str, Any]) -> None:
        personal_info = cv_data.get("personal_info", {})

        name = personal_info.get("name", "")
        if name:
            elements.append(Paragraph(escape_text_preserving_tags(name), styles["NameStyle"]))

        desired_role = get_localized_field(
            cv_data.get("desired_role", {}),
            "desired_role",
            self.language,
            "",
        )
        if desired_role:
            elements.append(Paragraph(escape_text_preserving_tags(desired_role), styles["TitleStyle"]))

        # Junta contatos em uma linha separada por `|` para leitura compacta.
        contact_items: list[str] = []
        phone_number = str(personal_info.get("phone", "")).strip()
        if phone_number:
            # Regra de negócio atual: quando idioma é inglês e faltou prefixo +55, prefixa.
            if self.language == "en" and not phone_number.startswith("+55"):
                phone_number = f"+55 {phone_number}"
            contact_items.append(phone_number)

        email = str(personal_info.get("email", "")).strip()
        if email:
            contact_items.append(email)

        location = str(personal_info.get("location", "")).strip()
        if location:
            contact_items.append(location)

        if contact_items:
            contact_text = " | ".join(contact_items)
            elements.append(Paragraph(escape_text_preserving_tags(contact_text), styles["ContactStyle"]))

        social_items = personal_info.get("social") or []
        if isinstance(social_items, list) and social_items:
            social_links: list[str] = []
            # Escapa atributos de cor para não quebrar a marcação XML interna do ReportLab.
            escaped_link_color = escape_xml_attribute(
                self.pdf_style_engine.social_link_color()
            )
            for social_item in social_items:
                if not isinstance(social_item, dict):
                    continue
                label = str(social_item.get("label", "")).strip()
                url = str(social_item.get("url", "")).strip()
                if not url:
                    continue

                # Escapa URL/label para evitar caracteres inválidos no elemento `<a>`.
                escaped_url = escape_xml_attribute(url)
                label_text = label or url
                escaped_label = escape_text_preserving_tags(label_text)
                social_links.append(
                    f'<a href="{escaped_url}" color="{escaped_link_color}">{escaped_label}</a>'
                )

            if social_links:
                elements.append(Paragraph(" | ".join(social_links), styles["ContactStyle"]))

        elements.append(Spacer(1, self.pdf_style_engine.spacing("header_bottom") * mm))

    # Propósito:
    # - inserir seção de resumo profissional, quando houver conteúdo.
    # Efeitos:
    # - adiciona elementos de título e corpo em `elements`.
    def _add_summary(self, elements: list[Any], styles: StyleSheet1, cv_data: dict[str, Any]) -> None:
        summary = get_localized_field(cv_data.get("summary", {}), "description", self.language, "")
        if not summary:
            # Sem resumo não há seção para renderizar.
            return

        # Título é traduzido conforme idioma selecionado.
        section_title = get_translation(
            self.translations,
            self.language,
            "sections",
            "summary",
            "Summary",
        )
        elements.append(Paragraph(escape_text_preserving_tags(section_title), styles["SectionTitleStyle"]))
        elements.append(Paragraph(process_rich_text(summary), styles["BodyStyle"]))
        elements.append(Spacer(1, self.pdf_style_engine.spacing("section_bottom") * mm))

    # Propósito:
    # - renderizar o título visível de cada seção dinâmica.
    # Efeitos:
    # - adiciona um `Paragraph` ao fluxo de elementos.
    def _add_section_title(self, elements: list[Any], styles: StyleSheet1, section_type: str) -> None:
        section_title = get_translation(
            self.translations,
            self.language,
            "sections",
            section_type,
            section_type,
        )
        elements.append(
            Paragraph(escape_text_preserving_tags(section_title), styles["SectionTitleStyle"])
        )
