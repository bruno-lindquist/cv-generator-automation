# Funcoes de localizacao para traducao, fallback de idioma e sanitizacao segura de texto.
from __future__ import annotations

import re
from typing import Any
from xml.sax.saxutils import escape

MONTHS_BY_LANGUAGE = {
    "pt": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}

TAG_MARKERS = {"<b>": "___BOLD_START___", "</b>": "___BOLD_END___", "<i>": "___ITALIC_START___", "</i>": "___ITALIC_END___", "<u>": "___UNDERLINE_START___", "</u>": "___UNDERLINE_END___"}

FILENAME_SANITIZATION_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
XML_ESCAPE_ENTITIES = {"'": "&apos;", '"': "&quot;"}


# Busca traducao aceitando schema antigo e novo, com fallback seguro para valor default.
def get_translation(
    translations: dict[str, Any],
    language: str,
    section: str,
    key: str,
    default: str,
) -> str:
    language_scope = translations.get(language)
    if isinstance(language_scope, dict):
        return language_scope.get(section, {}).get(key, default)

    section_scope = translations.get(section, {})
    if not isinstance(section_scope, dict):
        return default

    translated_value = section_scope.get(key)
    if isinstance(translated_value, dict) and _contains_language_variants(translated_value):
        selected_value = _select_language_variant(translated_value, language)
        return _normalize_string(selected_value, default)

    return _normalize_string(translated_value, default)


# Resolve campo localizado por idioma com fallback para portugues e valor neutro.
def get_localized_field(data: Any, field_name: str, language: str, default: str = "") -> str:
    if not isinstance(data, dict):
        return default

    field_value = data.get(field_name)
    if isinstance(field_value, dict) and _contains_language_variants(field_value):
        resolved_value = _select_language_variant(field_value, language)
        return _normalize_string(resolved_value, default)

    localized_value = data.get(f"{field_name}_{language}")
    portuguese_fallback = data.get(f"{field_name}_pt") if language != "pt" else None
    neutral_fallback = field_value

    resolved_value = localized_value or portuguese_fallback or neutral_fallback or ""
    return _normalize_string(resolved_value, default)


# Resolve listas localizadas preservando compatibilidade entre formatos legado e unificado.
def get_localized_list(data: Any, field_name: str, language: str) -> list[str]:
    if not isinstance(data, dict):
        return []

    field_value = data.get(field_name)
    if isinstance(field_value, dict) and _contains_language_variants(field_value):
        selected_list = _select_language_variant(field_value, language)
        if isinstance(selected_list, list):
            return [str(item) for item in selected_list]

    legacy_values = (
        data.get(f"{field_name}_{language}")
        or (data.get(f"{field_name}_pt") if language != "pt" else None)
        or data.get(field_name)
        or []
    )
    if not isinstance(legacy_values, list):
        return []

    return [str(item) for item in legacy_values]


# Escapa entidades XML sem remover tags de formatacao permitidas (<b>, <i>, <u>).
def escape_text_preserving_tags(raw_text: Any) -> str:
    text = str(raw_text)

    # Usa marcadores temporários para preservar apenas as tags permitidas.
    protected_text = text
    for tag, marker in TAG_MARKERS.items():
        protected_text = protected_text.replace(tag, marker)

    escaped_text = escape(protected_text, XML_ESCAPE_ENTITIES)

    for tag, marker in TAG_MARKERS.items():
        escaped_text = escaped_text.replace(marker, tag)

    return escaped_text


# Escapa conteudo para atributos XML, incluindo aspas simples e duplas.
def escape_xml_attribute(raw_value: Any) -> str:
    return escape(str(raw_value), XML_ESCAPE_ENTITIES)


# Prepara texto rico para Paragraph convertendo quebras de linha em <br/>.
def process_rich_text(raw_text: Any) -> str:
    return escape_text_preserving_tags(raw_text).replace("\n", "<br/>")


# Converte mes numerico para abreviacao local, mantendo valor original quando invalido.
def format_month(raw_month: Any, language: str) -> str:
    try:
        month_number = int(raw_month)
    except (TypeError, ValueError):
        return str(raw_month)

    if not 1 <= month_number <= 12:
        return str(raw_month)

    months = MONTHS_BY_LANGUAGE.get(language, MONTHS_BY_LANGUAGE["pt"])
    return months[month_number - 1]


# Monta periodo de inicio/fim usando traducao de "atual" quando nao houver data final.
def format_period(
    *,
    start_month: Any,
    start_year: Any,
    end_month: Any,
    end_year: Any,
    translations: dict[str, Any],
    language: str,
) -> str:
    initial_month = format_month(start_month, language)
    start_period = f"{initial_month} {start_year}".strip()

    if end_month and end_year:
        final_month = format_month(end_month, language)
        return f"{start_period} - {final_month} {end_year}".strip()

    current_label = get_translation(translations, language, "labels", "current", "Present")
    return f"{start_period} - {current_label}".strip()


# Limpa componente de nome de arquivo removendo caracteres inseguros.
def sanitize_filename_component(raw_value: Any, fallback: str = "CV") -> str:
    escaped_value = FILENAME_SANITIZATION_PATTERN.sub("_", str(raw_value).strip())
    normalized_value = escaped_value.strip("._-")
    return normalized_value or fallback


# Identifica dicionarios que seguem o padrao de variantes por idioma.
def _contains_language_variants(value: dict[str, Any]) -> bool:
    language_keys = {"pt", "en", "default"}
    return bool(language_keys.intersection(value.keys()))


# Define criterio unico de "valor preenchido" usado nas regras de fallback.
def _is_non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


# Seleciona a melhor variante disponivel seguindo ordem de prioridade por idioma.
def _select_language_variant(variants: dict[str, Any], language: str) -> Any:
    # Ordem de busca prioriza idioma pedido, depois fallbacks explícitos e padrão.
    lookup_order = [language]
    if language != "pt":
        lookup_order.append("pt")
    if language != "en":
        lookup_order.append("en")
    lookup_order.append("default")

    for language_key in lookup_order:
        value = variants.get(language_key)
        if _is_non_empty(value):
            return value

    for language_key in lookup_order:
        if language_key in variants:
            return variants[language_key]

    for fallback_value in variants.values():
        return fallback_value

    return None


# Converte qualquer valor para string limpa e aplica default quando necessario.
def _normalize_string(value: Any, default: str) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip() or default
    return str(value).strip() or default
