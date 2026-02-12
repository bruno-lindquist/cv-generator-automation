# Este arquivo concentra funções que extraem valores simples de estilo para o PDF.
# Ele serve para evitar repetição de validações ao ler `styles.json`.
# Organização:
# - funções públicas para margens, espaçamentos e cor de link social
# - função auxiliar privada para garantir que uma seção seja dicionário
# Entradas esperadas:
# - dicionário de configuração de estilos e chaves específicas
# Saídas esperadas:
# - valores já convertidos/validados (float ou str)
# - em caso de inconsistência, lança `PdfRenderError`

from __future__ import annotations

from typing import Any

from infrastructure.pdf_styles.style_validation_helpers import require_dictionary_section
from shared.exceptions import PdfRenderError


# Propósito:
# - obter uma margem obrigatória em `style_configuration["margins"]`.
# Retorno:
# - valor da margem convertido para `float`.
def resolve_margin_value(style_configuration: dict[str, Any], margin_key: str) -> float:
    # Garante que a seção `margins` exista e tenha formato correto.
    margins_section = require_dictionary_section(
        style_configuration,
        "margins",
        "Style configuration missing 'margins' dictionary in styles.json",
    )
    # Busca a margem pedida (ex.: "top", "bottom", "left", "right").
    margin_value = margins_section.get(margin_key)
    if margin_value is None:
        raise PdfRenderError(
            f"Style configuration missing 'margins.{margin_key}' in styles.json"
        )
    # Converte para float para uso consistente pelo motor de PDF.
    return float(margin_value)


# Propósito:
# - obter um espaçamento obrigatório em `style_configuration["spacing"]`.
# Retorno:
# - valor de espaçamento convertido para `float`.
def resolve_spacing_value(style_configuration: dict[str, Any], spacing_key: str) -> float:
    # Reutiliza validação centralizada para garantir que `spacing` é dicionário.
    spacing_section = require_dictionary_section(
        style_configuration,
        "spacing",
        "Style configuration missing 'spacing' dictionary in styles.json",
    )
    # Busca chave específica de espaçamento (ex.: "section_bottom", "item_bottom").
    spacing_value = spacing_section.get(spacing_key)
    if spacing_value is None:
        raise PdfRenderError(
            f"Style configuration missing 'spacing.{spacing_key}' in styles.json"
        )
    return float(spacing_value)


# Propósito:
# - obter a cor usada nos links sociais (ex.: LinkedIn/GitHub no cabeçalho).
# Retorno:
# - string com valor da cor (hexadecimal, nome etc., conforme estilo).
def resolve_social_link_color(style_configuration: dict[str, Any]) -> str:
    # Seção `links` precisa existir para conter estilos de hyperlink.
    links_section = require_dictionary_section(
        style_configuration,
        "links",
        "Style configuration missing 'links' dictionary in styles.json",
    )
    link_color = links_section.get("social_link_color")
    # Exige texto não vazio para evitar gerar tags de link inválidas no PDF.
    if not isinstance(link_color, str) or not link_color.strip():
        raise PdfRenderError(
            "Style configuration missing 'links.social_link_color' in styles.json"
        )
    return link_color
