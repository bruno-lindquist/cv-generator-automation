# Contrato base e utilitarios compartilhados para transformar itens de secao em elementos PDF.
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from reportlab.lib.styles import StyleSheet1
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from localization import (
    escape_text_preserving_tags,
    format_period,
    get_localized_field,
    get_localized_list,
    process_rich_text,
)
from infrastructure.pdf_styles import PdfStyleEngine


# Extrai inicio/fim do item e delega a formatacao de periodo para utilitario comum.
def build_period_text(
    section_item: dict[str, Any],
    translations: dict[str, Any],
    language: str,
) -> str:
    # Campos ausentes viram string vazia para manter formato robusto.
    return format_period(
        start_month=section_item.get("start_month", ""),
        start_year=section_item.get("start_year", ""),
        end_month=section_item.get("end_month", ""),
        end_year=section_item.get("end_year", ""),
        translations=translations,
        language=language,
    )


# Contrato base com helpers de localizacao e montagem de paragrafo para todas as secoes.
class BaseSectionFormatter(ABC):

    # Armazena idioma, traducoes e motor de estilos compartilhados por cada item renderizado.
    def __init__(
        self,
        *,
        language: str,
        translations: dict[str, Any],
        pdf_style_engine: PdfStyleEngine,
    ) -> None:
        self.language = language
        self.translations = translations
        self.pdf_style_engine = pdf_style_engine

    # Metodo abstrato que obriga cada secao concreta a definir sua propria renderizacao.
    @abstractmethod
    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        # Define o contrato de formatacao que deve ser implementado pelas subclasses.
        pass

    # Resolve um campo textual localizado para o idioma ativo da renderizacao.
    def localized_field(
        self,
        section_item: dict[str, Any],
        field_name: str,
        default: str = "",
    ) -> str:
        return get_localized_field(section_item, field_name, self.language, default)

    # Resolve uma lista localizada para o idioma ativo da renderizacao.
    def localized_list(self, section_item: dict[str, Any], field_name: str) -> list[str]:
        return get_localized_list(section_item, field_name, self.language)

    # Adiciona paragrafo em negrito apenas quando houver texto util.
    def add_bold_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        text: str,
        style_name: str,
    ) -> None:
        if text:
            safe_text = escape_text_preserving_tags(text)
            elements.append(Paragraph(f"<b>{safe_text}</b>", styles[style_name]))

    # Adiciona paragrafo em italico apenas quando houver texto util.
    def add_italic_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        text: str,
        style_name: str,
    ) -> None:
        if text:
            safe_text = escape_text_preserving_tags(text)
            elements.append(Paragraph(f"<i>{safe_text}</i>", styles[style_name]))

    # Adiciona paragrafo simples com escape para evitar markup invalida no PDF.
    def add_plain_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        text: str,
        style_name: str,
    ) -> None:
        if text:
            elements.append(Paragraph(escape_text_preserving_tags(text), styles[style_name]))

    # Combina titulo e detalhe sem gerar separador sobrando quando um lado estiver vazio.
    def compose_bold_with_detail_text(
        self,
        bold_text: str,
        detail_text: str,
        *,
        separator: str = " - ",
    ) -> str:
        safe_bold_text = escape_text_preserving_tags(bold_text)
        safe_detail_text = escape_text_preserving_tags(detail_text)
        # Evita inserir separador quando apenas um dos lados possui conteúdo.
        if safe_bold_text and safe_detail_text:
            return f"<b>{safe_bold_text}</b>{separator}{safe_detail_text}"
        return safe_bold_text or safe_detail_text

    # Insere texto rico no estilo de corpo mantendo padrao visual da secao.
    def add_body_rich_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        rich_text: str,
    ) -> None:
        if rich_text:
            elements.append(Paragraph(rich_text, styles["BodyStyle"]))

    # Compoe e adiciona linha com texto principal e detalhe usando a mesma regra de formatacao.
    def add_composite_body_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        *,
        main_text: str,
        detail_text: str,
        separator: str = " - ",
    ) -> None:
        composite_text = self.compose_bold_with_detail_text(
            main_text,
            detail_text,
            separator=separator,
        )
        self.add_body_rich_paragraph(elements, styles, composite_text)

    # Renderiza descricoes como lista com bullet e suporte a quebra de linha/rich text.
    def add_bullet_descriptions(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        descriptions: list[str],
    ) -> None:
        for description in descriptions:
            elements.append(Paragraph(f"• {process_rich_text(description)}", styles["BodyStyle"]))

    # Aplica espacamento vertical por chave sem espalhar valores numericos no codigo.
    def add_spacing(self, elements: list[Any], spacing_key: str) -> None:
        spacing_value = self.pdf_style_engine.spacing(spacing_key)
        elements.append(Spacer(1, spacing_value * mm))

    # Renderiza titulo de categoria apenas quando o campo estiver preenchido.
    def add_category_title(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
        *,
        field_name: str = "category",
        style_name: str = "ItemTitleStyle",
    ) -> None:
        category = self.localized_field(section_item, field_name)
        if category:
            self.add_plain_paragraph(elements, styles, category, style_name)

    # Renderiza colecao em linha unica separada por virgulas para leitura rapida.
    def add_comma_separated_values(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        values: list[Any],
        *,
        style_name: str = "BodyStyle",
    ) -> None:
        if values:
            text = ", ".join(str(value) for value in values)
            self.add_plain_paragraph(elements, styles, text, style_name)
