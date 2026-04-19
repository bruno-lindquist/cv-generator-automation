# Funcoes de localizacao para traducao, fallback de idioma e sanitizacao segura de texto.
from __future__ import annotations

import re
from typing import Any, TypeGuard
from xml.sax.saxutils import escape

# Idioma padrao usado nos fallbacks de traducao e selecao de variantes.
DEFAULT_LANGUAGE = "pt"

MONTHS_BY_LANGUAGE = {
    "pt": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}

TAG_MARKERS = {
    "<b>": "___BOLD_START___",
    "</b>": "___BOLD_END___",
    "<i>": "___ITALIC_START___",
    "</i>": "___ITALIC_END___",
    "<u>": "___UNDERLINE_START___",
    "</u>": "___UNDERLINE_END___",
}

FILENAME_SANITIZATION_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
XML_ESCAPE_ENTITIES = {"'": "&apos;", '"': "&quot;"}


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

    value = section_scope.get(key)
    if _is_variant_dict(value):
        value = _select_language_variant(value, language)
    return _coerce_string(value, default)


def get_localized_field(data: Any, field_name: str, language: str, default: str = "") -> str:
    if not isinstance(data, dict):
        return default

    field_value = data.get(field_name)
    if _is_variant_dict(field_value):
        return _coerce_string(_select_language_variant(field_value, language), default)

    resolved_value = (
        data.get(f"{field_name}_{language}")
        or _default_language_fallback(data, field_name, language)
        or field_value
        or ""
    )
    return _coerce_string(resolved_value, default)


def get_localized_list(data: Any, field_name: str, language: str) -> list[str]:
    if not isinstance(data, dict):
        return []

    field_value = data.get(field_name)
    if _is_variant_dict(field_value):
        selected = _select_language_variant(field_value, language)
        return [str(item) for item in selected] if isinstance(selected, list) else []

    legacy_values = (
        data.get(f"{field_name}_{language}")
        or _default_language_fallback(data, field_name, language)
        or field_value
        or []
    )
    if not isinstance(legacy_values, list):
        return []

    return [str(item) for item in legacy_values]


# Escapa entidades XML sem remover tags de formatacao permitidas (<b>, <i>, <u>).
def escape_text_preserving_tags(raw_text: Any) -> str:
    protected_text = str(raw_text)
    for tag, marker in TAG_MARKERS.items():
        protected_text = protected_text.replace(tag, marker)

    escaped_text = escape(protected_text, XML_ESCAPE_ENTITIES)

    for tag, marker in TAG_MARKERS.items():
        escaped_text = escaped_text.replace(marker, tag)

    return escaped_text


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
    formatted_start_month = format_month(start_month, language)
    start_period = f"{formatted_start_month} {start_year}".strip()

    if end_year:
        formatted_end_month = format_month(end_month, language) if end_month else ""
        end_period = f"{formatted_end_month} {end_year}".strip()
        return f"{start_period} - {end_period}"

    current_label = get_translation(translations, language, "labels", "current", "Present")
    return f"{start_period} - {current_label}".strip()


def sanitize_filename_component(raw_value: Any, fallback: str = "CV") -> str:
    escaped_value = FILENAME_SANITIZATION_PATTERN.sub("_", str(raw_value).strip())
    return escaped_value.strip("._-") or fallback


# Identifica dicionarios que seguem o padrao de variantes por idioma.
def _is_variant_dict(value: Any) -> TypeGuard[dict[str, Any]]:
    return isinstance(value, dict) and not {"pt", "en", "default"}.isdisjoint(value.keys())


def _is_non_empty(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list | dict):
        return len(value) > 0
    return value is not None


def _default_language_fallback(data: dict[str, Any], field_name: str, language: str) -> Any:
    if language == DEFAULT_LANGUAGE:
        return None
    return data.get(f"{field_name}_{DEFAULT_LANGUAGE}")


# Seleciona a melhor variante disponivel seguindo ordem de prioridade por idioma.
def _select_language_variant(variants: dict[str, Any], language: str) -> Any:
    lookup_order = [language]
    if language != DEFAULT_LANGUAGE:
        lookup_order.append(DEFAULT_LANGUAGE)
    if language != "en":
        lookup_order.append("en")
    lookup_order.append("default")

    for language_key in lookup_order:
        if _is_non_empty(variants.get(language_key)):
            return variants[language_key]

    for language_key in lookup_order:
        if language_key in variants:
            return variants[language_key]

    return next(iter(variants.values()), None)


def _coerce_string(value: Any, default: str) -> str:
    if value is None:
        return default
    text = value if isinstance(value, str) else str(value)
    return text.strip() or default
