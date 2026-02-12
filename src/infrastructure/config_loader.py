# Este arquivo carrega e valida a configuração principal da aplicação.
# Ele serve para transformar o JSON bruto do `config.json` em objetos tipados.
# Organização:
# - dataclasses de configuração (`FileSettings`, `DefaultSettings`, `LoggingSettings`)
# - função pública `load_app_config` (entrada principal)
# - funções internas de parsing e validação
# Entradas esperadas:
# - caminho para arquivo JSON de configuração
# Saídas esperadas:
# - objeto `AppConfig` com dados já validados e normalizados
# - em caso de inconsistência, lança `ConfigurationError`

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shared.exceptions import ConfigurationError


# Representa configurações de arquivos (origem de dados, estilos e diretório de saída).
# `frozen=True` torna a instância imutável: depois de criada, os campos não mudam.
@dataclass(frozen=True)
class FileSettings:
    data: str
    data_by_language: dict[str, str] | None
    styles: str
    translations: str
    translations_by_language: dict[str, str] | None
    output_dir: str


# Representa valores padrão usados pela aplicação (idioma e encoding).
@dataclass(frozen=True)
class DefaultSettings:
    language: str
    encoding: str


# Representa configurações de logging (se ativa, nível e diretório de logs).
@dataclass(frozen=True)
class LoggingSettings:
    enabled: bool
    level: str
    directory: str


# Agrega todas as seções em uma única configuração de alto nível.
@dataclass(frozen=True)
class AppConfig:
    files: FileSettings
    defaults: DefaultSettings
    logging: LoggingSettings


# Propósito:
# - carregar o JSON de configuração do disco e validar sua estrutura.
# Retorno:
# - `AppConfig` pronto para uso no restante da aplicação.
# Efeitos:
# - lê arquivo no sistema de arquivos.
# - pode lançar `ConfigurationError` quando há ausência de arquivo ou JSON inválido.
def load_app_config(config_file_path: Path) -> AppConfig:
    # Normaliza o caminho para evitar ambiguidades e facilitar mensagens de erro.
    resolved_config_path = config_file_path.expanduser().resolve()

    # Validação explícita para erro mais amigável que um FileNotFoundError genérico.
    if not resolved_config_path.exists():
        raise ConfigurationError(f"Configuration file not found: {resolved_config_path}")

    try:
        # Carrega o conteúdo bruto do JSON para um dicionário Python.
        with resolved_config_path.open("r", encoding="utf-8") as config_file:
            raw_config = json.load(config_file)
    except json.JSONDecodeError as exc:
        # Repassa o erro com contexto de domínio da aplicação.
        raise ConfigurationError(
            f"Configuration file has invalid JSON: {resolved_config_path}"
        ) from exc

    return _parse_config(raw_config)


# Propósito:
# - validar regras de presença/tipo e montar objetos dataclass de configuração.
# Retorno:
# - instância de `AppConfig`.
# Efeitos:
# - não grava arquivos; apenas valida e cria objetos em memória.
def _parse_config(raw_config: dict[str, Any]) -> AppConfig:
    files_section = raw_config.get("files")
    defaults_section = raw_config.get("defaults", {})
    logging_section = raw_config.get("logging", {})

    # A seção `files` é obrigatória porque define os caminhos principais da aplicação.
    if not isinstance(files_section, dict):
        raise ConfigurationError("Missing required 'files' section in config")

    # Chaves mínimas exigidas para o sistema funcionar.
    required_file_keys = ["styles", "output_dir"]
    missing_file_keys = [
        key for key in required_file_keys if not files_section.get(key)
    ]
    # Aqui aceitamos duas estratégias:
    # - caminho único (`data` / `translations`)
    # - mapeamento por idioma (`*_by_language`)
    has_data_mapping = isinstance(files_section.get("data_by_language"), dict)
    has_translations_mapping = isinstance(
        files_section.get("translations_by_language"),
        dict,
    )
    if not files_section.get("data") and not has_data_mapping:
        missing_file_keys.append("data or data_by_language")
    if not files_section.get("translations") and not has_translations_mapping:
        missing_file_keys.append("translations or translations_by_language")

    if missing_file_keys:
        missing_keys_str = ", ".join(missing_file_keys)
        raise ConfigurationError(
            f"Missing required config keys in 'files': {missing_keys_str}"
        )

    # Valida e normaliza mapeamentos opcionais por idioma.
    data_by_language = _parse_language_mapping(
        files_section.get("data_by_language"),
        "data_by_language",
    )
    translations_by_language = _parse_language_mapping(
        files_section.get("translations_by_language"),
        "translations_by_language",
    )

    # Monta objeto tipado da seção de arquivos.
    file_settings = FileSettings(
        data=str(files_section.get("data", "")),
        data_by_language=data_by_language,
        styles=str(files_section["styles"]),
        translations=str(files_section.get("translations", "")),
        translations_by_language=translations_by_language,
        output_dir=str(files_section["output_dir"]),
    )

    # Define defaults quando valores não são informados no JSON.
    default_settings = DefaultSettings(
        language=str(defaults_section.get("language", "pt")).lower(),
        encoding=str(defaults_section.get("encoding", "utf-8")),
    )

    # Normaliza nível para maiúsculo por convenção de logging.
    logging_settings = LoggingSettings(
        enabled=bool(logging_section.get("enabled", True)),
        level=str(logging_section.get("level", "INFO")).upper(),
        directory=str(logging_section.get("directory", "logs")),
    )

    return AppConfig(
        files=file_settings,
        defaults=default_settings,
        logging=logging_settings,
    )


# Propósito:
# - validar um dicionário `{idioma: caminho}` e normalizar chaves de idioma.
# Retorno:
# - `dict[str, str]` validado, ou `None` quando a chave não foi informada.
def _parse_language_mapping(
    raw_mapping: Any,
    mapping_key: str,
) -> dict[str, str] | None:
    # `None` significa "não configurado", e isso é permitido.
    if raw_mapping is None:
        return None

    # Exige estrutura de dicionário para permitir busca por código de idioma.
    if not isinstance(raw_mapping, dict):
        raise ConfigurationError(f"Key '{mapping_key}' must be a dictionary")

    parsed_mapping: dict[str, str] = {}
    for language_code, file_path in raw_mapping.items():
        # Código de idioma precisa ser texto (ex.: "pt", "en", "es").
        if not isinstance(language_code, str):
            raise ConfigurationError(
                f"Key '{mapping_key}' has non-string language code"
            )
        # Caminho deve ser string não vazia.
        if not isinstance(file_path, str) or not file_path.strip():
            raise ConfigurationError(
                f"Key '{mapping_key}' has invalid path for language '{language_code}'"
            )
        # Normaliza para minúsculo para evitar duplicidade "PT" vs "pt".
        parsed_mapping[language_code.lower()] = file_path

    # Evita configuração vazia que não serviria para seleção de idioma.
    if not parsed_mapping:
        raise ConfigurationError(f"Key '{mapping_key}' cannot be empty")

    return parsed_mapping
