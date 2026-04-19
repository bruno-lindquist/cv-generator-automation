# Resolve caminhos do projeto a partir da configuracao, separando responsabilidade do serviço principal.
from __future__ import annotations

from pathlib import Path
from typing import Any

from exceptions import ConfigurationError, OutputPathError
from localization import DEFAULT_LANGUAGE, get_localized_field, sanitize_filename_component


class CvPathResolver:
    def __init__(self, *, config_directory: Path) -> None:
        self.config_directory = config_directory

    # Normaliza caminhos recebidos em runtime para forma absoluta.
    def resolve_runtime_path(self, raw_path: str | Path) -> Path:
        return Path(raw_path).expanduser().resolve()

    # Resolve caminhos relativos ao diretorio do config, preservando caminhos absolutos.
    def resolve_config_relative_path(self, raw_path: str | Path) -> Path:
        candidate_path = Path(raw_path).expanduser()
        if candidate_path.is_absolute():
            return candidate_path.resolve()
        return (self.config_directory / candidate_path).resolve()

    # Aplica prioridade entre caminho direto e mapeamento por idioma.
    def resolve_language_aware_path(
        self,
        *,
        direct_path: str,
        path_by_language: dict[str, str] | None,
        language: str,
        path_label: str,
    ) -> Path:
        if direct_path:
            return self.resolve_config_relative_path(direct_path)
        mapped_path = (path_by_language or {}).get(language)
        if mapped_path:
            return self.resolve_config_relative_path(mapped_path)
        raise ConfigurationError(f"No {path_label} file configured for language '{language}'")

    # Monta nome final do PDF a partir dos dados do candidato, impedindo path traversal.
    def build_output_file_path(
        self,
        *,
        cv_data: dict[str, Any],
        language: str,
        output_dir_config: str,
    ) -> Path:
        output_root_directory = self.resolve_config_relative_path(output_dir_config)
        output_root_directory.mkdir(parents=True, exist_ok=True)

        personal_info = cv_data.get("personal_info", {})
        desired_role = cv_data.get("desired_role", {})
        english_role_component = sanitize_filename_component(
            get_localized_field(desired_role, "desired_role", "en", "CV"),
            fallback="CV",
        )
        role_output_directory = output_root_directory / english_role_component
        role_output_directory.mkdir(parents=True, exist_ok=True)

        name_component = sanitize_filename_component(
            personal_info.get("name", "CV"),
            fallback="CV",
        )
        role_component = sanitize_filename_component(
            get_localized_field(desired_role, "desired_role", language, "CV"),
            fallback="CV",
        )
        language_suffix = "" if language == DEFAULT_LANGUAGE else f"_{language.upper()}"
        candidate_output_path = (
            role_output_directory / f"{name_component}_{role_component}{language_suffix}.pdf"
        )
        resolved_output_path = candidate_output_path.resolve()

        if role_output_directory.resolve() not in resolved_output_path.parents:
            raise OutputPathError("Generated output path escaped output directory")
        return resolved_output_path
