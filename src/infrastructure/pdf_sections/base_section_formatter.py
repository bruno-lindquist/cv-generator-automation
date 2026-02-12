"""Base abstractions and shared helpers for PDF section formatters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from reportlab.lib.styles import StyleSheet1
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer

from domain.localization import (
    escape_text_preserving_tags,
    get_localized_field,
    get_localized_list,
    process_rich_text,
)
from infrastructure.pdf_styles import PdfStyleEngine


class BaseSectionFormatter(ABC):
    """Contract and reusable utilities for section-specific PDF formatters."""

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

    @abstractmethod
    def format_section_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        section_item: dict[str, Any],
    ) -> None:
        """Append one section item into the reportlab elements list."""

    def localized_field(
        self,
        section_item: dict[str, Any],
        field_name: str,
        default: str = "",
    ) -> str:
        return get_localized_field(section_item, field_name, self.language, default)

    def localized_list(self, section_item: dict[str, Any], field_name: str) -> list[str]:
        return get_localized_list(section_item, field_name, self.language)

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

    def add_plain_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        text: str,
        style_name: str,
    ) -> None:
        if text:
            elements.append(Paragraph(escape_text_preserving_tags(text), styles[style_name]))

    def compose_bold_with_detail_text(
        self,
        bold_text: str,
        detail_text: str,
        *,
        separator: str = " - ",
    ) -> str:
        safe_bold_text = escape_text_preserving_tags(bold_text)
        safe_detail_text = escape_text_preserving_tags(detail_text)
        if safe_bold_text and safe_detail_text:
            return f"<b>{safe_bold_text}</b>{separator}{safe_detail_text}"
        return safe_bold_text or safe_detail_text

    def add_body_rich_paragraph(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        rich_text: str,
    ) -> None:
        if rich_text:
            elements.append(Paragraph(rich_text, styles["BodyStyle"]))

    def add_bullet_descriptions(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        descriptions: list[str],
    ) -> None:
        for description in descriptions:
            elements.append(Paragraph(f"• {process_rich_text(description)}", styles["BodyStyle"]))

    def add_spacing(self, elements: list[Any], spacing_key: str) -> None:
        spacing_value = self.pdf_style_engine.spacing(spacing_key)
        elements.append(Spacer(1, spacing_value * mm))
