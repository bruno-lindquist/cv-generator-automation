# Valida e converte o JSON de estilos para objetos ReportLab usados no documento final.
from __future__ import annotations

from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet

from exceptions import PdfRenderError

_STYLES_FILENAME = "styles.json"

_STYLE_FIELD_MAPPING = {
    "font_name": "fontName",
    "font_size": "fontSize",
    "text_color": "textColor",
    "space_before": "spaceBefore",
    "space_after": "spaceAfter",
    "left_indent": "leftIndent",
    "alignment": "alignment",
    "keep_with_next": "keepWithNext",
}
_ALIGNMENT_BY_NAME = {
    "left": TA_LEFT,
    "center": TA_CENTER,
    "right": TA_RIGHT,
    "justify": TA_JUSTIFY,
}
REQUIRED_PARAGRAPH_STYLE_NAMES = [
    "NameStyle",
    "TitleStyle",
    "SectionTitleStyle",
    "ItemTitleStyle",
    "ItemSubtitleStyle",
    "BodyStyle",
    "ContactStyle",
    "DateStyle",
]
_REQUIRED_MARGIN_KEYS = ["top", "bottom", "left", "right"]
_REQUIRED_SPACING_KEYS = [
    "header_bottom",
    "section_bottom",
    "item_bottom",
    "small_bottom",
    "minimal_bottom",
]


def _missing(path: str) -> PdfRenderError:
    return PdfRenderError(f"Style configuration missing '{path}' in {_STYLES_FILENAME}")


# Garante que a secao exista como dicionario antes de acessar suas chaves.
def _require_section(style_configuration: dict[str, Any], section_key: str) -> dict[str, Any]:
    section = style_configuration.get(section_key)
    if not isinstance(section, dict):
        raise PdfRenderError(
            f"Style configuration missing '{section_key}' dictionary in {_STYLES_FILENAME}"
        )
    return section


# Valida presenca de todas as chaves esperadas em uma secao.
def _require_keys(section: dict[str, Any], section_key: str, required_keys: list[str]) -> None:
    for key in required_keys:
        if section.get(key) is None:
            raise _missing(f"{section_key}.{key}")


# Valida a cor de link social, usada tambem como parte da validacao inicial.
def _require_social_link_color(links: dict[str, Any]) -> str:
    value = links.get("social_link_color")
    if not isinstance(value, str) or not value.strip():
        raise _missing("links.social_link_color")
    return value


# Garante presenca de secoes e chaves obrigatorias antes de iniciar renderizacao.
def _validate_style_configuration(style_configuration: dict[str, Any]) -> None:
    paragraph_styles = _require_section(style_configuration, "paragraph_styles")
    missing_styles = [
        name for name in REQUIRED_PARAGRAPH_STYLE_NAMES if name not in paragraph_styles
    ]
    if missing_styles:
        raise PdfRenderError(
            f"Style configuration missing required paragraph styles: {', '.join(missing_styles)}"
        )
    _require_keys(
        _require_section(style_configuration, "margins"), "margins", _REQUIRED_MARGIN_KEYS
    )
    _require_keys(
        _require_section(style_configuration, "spacing"), "spacing", _REQUIRED_SPACING_KEYS
    )
    _require_social_link_color(_require_section(style_configuration, "links"))


def _resolve_alignment(alignment_value: Any) -> int:
    if isinstance(alignment_value, int):
        return alignment_value
    if not isinstance(alignment_value, str):
        return TA_LEFT
    return _ALIGNMENT_BY_NAME.get(alignment_value.lower(), TA_LEFT)


def _resolve_color(color_value: Any) -> colors.Color:
    if not isinstance(color_value, str) or not color_value.strip():
        raise PdfRenderError("Paragraph style 'text_color' must be a non-empty string")
    try:
        return colors.toColor(color_value)
    except ValueError as parse_error:
        raise PdfRenderError(f"Invalid paragraph style color: {color_value}") from parse_error


# Coerce por chave: apenas alignment e text_color precisam de tratamento; demais sao passthrough.
_FIELD_COERCERS = {
    "alignment": _resolve_alignment,
    "text_color": _resolve_color,
}


def _build_paragraph_style_kwargs(style_definition: dict[str, Any]) -> dict[str, Any]:
    return {
        reportlab_key: _FIELD_COERCERS.get(setting_key, lambda v: v)(style_definition[setting_key])
        for setting_key, reportlab_key in _STYLE_FIELD_MAPPING.items()
        if setting_key in style_definition
    }


# Transforma definicoes do JSON em ParagraphStyle compreensivel pelo ReportLab.
def _build_pdf_stylesheet(style_configuration: dict[str, Any]) -> StyleSheet1:
    paragraph_styles = style_configuration["paragraph_styles"]
    stylesheet = getSampleStyleSheet()

    for style_name, style_definition in paragraph_styles.items():
        if not isinstance(style_name, str) or not isinstance(style_definition, dict):
            continue
        if style_name in stylesheet.byName:
            continue

        parent_name = str(style_definition.get("parent", "Normal"))
        if parent_name not in stylesheet.byName:
            raise PdfRenderError(
                f"Style '{style_name}' references parent '{parent_name}' which is not "
                "registered (either built-in or a previously-defined custom style)"
            )
        stylesheet.add(
            ParagraphStyle(
                name=style_name,
                parent=stylesheet[parent_name],
                **_build_paragraph_style_kwargs(style_definition),
            )
        )

    return stylesheet


# Fachada de acesso semantico para margens, espacamentos e estilos ja validados.
class PdfStyleEngine:
    def __init__(self, style_configuration: dict[str, Any]) -> None:
        self.style_configuration = (
            style_configuration if isinstance(style_configuration, dict) else {}
        )
        _validate_style_configuration(self.style_configuration)
        # Sub-dicionarios ja validados: acesso direto evita re-checagem.
        self._margins: dict[str, Any] = self.style_configuration["margins"]
        self._spacing: dict[str, Any] = self.style_configuration["spacing"]
        self._links: dict[str, Any] = self.style_configuration["links"]
        self._stylesheet: StyleSheet1 | None = None

    # Constroi stylesheet ReportLab uma unica vez e reaproveita nas chamadas seguintes.
    def build_stylesheet(self) -> StyleSheet1:
        if self._stylesheet is None:
            self._stylesheet = _build_pdf_stylesheet(self.style_configuration)
        return self._stylesheet

    def margin(self, margin_key: str) -> float:
        return self._required_float(self._margins, "margins", margin_key)

    def spacing(self, spacing_key: str) -> float:
        return self._required_float(self._spacing, "spacing", spacing_key)

    def social_link_color(self) -> str:
        return _require_social_link_color(self._links)

    @staticmethod
    def _required_float(section: dict[str, Any], section_name: str, key: str) -> float:
        value = section.get(key)
        if value is None:
            raise _missing(f"{section_name}.{key}")
        return float(value)
