"""Application service that orchestrates CV generation."""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from domain.localization import get_localized_field, sanitize_filename_component
from domain.validators import validate_cv_data
from infrastructure.config_loader import AppConfig, load_app_config
from infrastructure.json_repository import JsonRepository
from infrastructure.pdf_renderer import CvPdfRenderer
from shared.exceptions import OutputPathError
from shared.logging_config import bind_logger_context, configure_logging


class CvGenerationService:
    """Use-case layer for generating CV PDFs."""

    def __init__(self, config_file_path: str | Path) -> None:
        self.config_file_path = Path(config_file_path).expanduser().resolve()
        self.config: AppConfig = load_app_config(self.config_file_path)
        self.config_directory = self.config_file_path.parent

        logs_directory = self._resolve_config_relative_path(
            self.config.logging.directory
        )
        configure_logging(
            level=self.config.logging.level,
            enabled=self.config.logging.enabled,
            logs_directory=logs_directory,
        )

    def generate(
        self,
        *,
        language: str | None,
        input_file_path: str | None,
        output_file_path: str | None,
    ) -> Path:
        effective_language = (language or self.config.defaults.language).lower()
        generation_request_id = uuid.uuid4().hex[:8]

        if input_file_path:
            data_file_path = self._resolve_runtime_path(input_file_path)
        else:
            data_file_path = self._resolve_language_aware_data_path(
                effective_language
            )

        visual_settings_path = self._resolve_config_relative_path(
            self.config.files.styles
        )
        translations_path = self._resolve_language_aware_translations_path(
            effective_language
        )

        started_at = time.perf_counter()
        repository = JsonRepository(encoding=self.config.defaults.encoding)

        cv_data = repository.load_json(data_file_path)
        visual_settings = repository.load_json(visual_settings_path)
        translations = repository.load_json(translations_path)

        if output_file_path:
            output_path = self._resolve_runtime_path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = self._build_output_file_path(
                cv_data=cv_data,
                language=effective_language,
            )

        contextual_logger = bind_logger_context(
            request_id=generation_request_id,
            language=effective_language,
            input_file=str(data_file_path),
            output_file=str(output_path),
        )
        contextual_logger.bind(event="app_start", step="cv_service").info(
            "Starting CV generation workflow"
        )

        validate_cv_data(cv_data)
        contextual_logger.bind(event="input_validated", step="validators").info(
            "Input data validated successfully"
        )

        pdf_renderer = CvPdfRenderer(
            language=effective_language,
            translations=translations,
            visual_settings=visual_settings,
        )

        generated_pdf_path = pdf_renderer.render_cv(
            cv_data=cv_data,
            output_file_path=output_path,
            app_logger=contextual_logger,
        )

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        contextual_logger.bind(
            event="app_finished",
            step="cv_service",
            duration_ms=str(elapsed_ms),
        ).info("CV generation workflow finished")

        return generated_pdf_path

    def _build_output_file_path(self, *, cv_data: dict[str, Any], language: str) -> Path:
        output_directory = self._resolve_config_relative_path(
            self.config.files.output_dir
        )
        output_directory.mkdir(parents=True, exist_ok=True)

        personal_info = cv_data.get("personal_info", {})
        desired_role = cv_data.get("desired_role", {})

        name_component = sanitize_filename_component(personal_info.get("name", "CV"), fallback="CV")
        role_component = sanitize_filename_component(
            get_localized_field(desired_role, "desired_role", language, "CV"),
            fallback="CV",
        )
        language_suffix = "" if language == "pt" else f"_{language.upper()}"

        candidate_output_path = output_directory / f"{name_component}_{role_component}{language_suffix}.pdf"
        resolved_output_path = candidate_output_path.resolve()

        if output_directory.resolve() not in resolved_output_path.parents:
            raise OutputPathError("Generated output path escaped output directory")

        return resolved_output_path

    def _resolve_language_aware_data_path(self, language: str) -> Path:
        if self.config.files.data:
            return self._resolve_config_relative_path(self.config.files.data)

        data_mapping = self.config.files.data_by_language or {}
        mapped_path = data_mapping.get(language)
        if mapped_path:
            return self._resolve_config_relative_path(mapped_path)

        raise OutputPathError(
            f"No data file configured for language '{language}'"
        )

    def _resolve_language_aware_translations_path(self, language: str) -> Path:
        if self.config.files.translations:
            return self._resolve_config_relative_path(
                self.config.files.translations
            )

        translations_mapping = self.config.files.translations_by_language or {}
        mapped_path = translations_mapping.get(language)
        if mapped_path:
            return self._resolve_config_relative_path(mapped_path)

        raise OutputPathError(
            f"No translations file configured for language '{language}'"
        )

    def _resolve_runtime_path(self, raw_path: str | Path) -> Path:
        candidate_path = Path(raw_path).expanduser()
        if candidate_path.is_absolute():
            return candidate_path.resolve()
        return candidate_path.resolve()

    def _resolve_config_relative_path(self, raw_path: str | Path) -> Path:
        candidate_path = Path(raw_path).expanduser()
        if candidate_path.is_absolute():
            return candidate_path.resolve()
        return (self.config_directory / candidate_path).resolve()


def run_generation(
    *,
    config_file_path: str | Path,
    language: str | None,
    input_file_path: str | None,
    output_file_path: str | None,
) -> Path:
    """Convenience function used by CLI and tests."""
    service = CvGenerationService(config_file_path=config_file_path)
    generated_path = service.generate(
        language=language,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
    )
    logger.bind(event="app_finished", step="entrypoint").info(
        f"Generated file: {generated_path}"
    )
    return generated_path
