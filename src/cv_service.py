# Caso de uso principal que coordena configuracao, leitura de dados e geracao final do PDF.
from __future__ import annotations

import time
from pathlib import Path
from shutil import copy2

from loguru import logger

from infrastructure.config_loader import AppConfig, load_app_config
from infrastructure.json_repository import load_json
from infrastructure.pdf_renderer import CvPdfRenderer
from logging_config import bind_logger_context, configure_logging
from path_resolver import CvPathResolver
from validators import validate_cv_data


# Coordena todo o pipeline de geracao: caminhos, validacao, renderizacao e observabilidade.
class CvGenerationService:
    # Carrega configuracao para disponibilizar defaults e caminhos ao pipeline de geracao.
    def __init__(self, config_file_path: str | Path) -> None:
        self.config_file_path = Path(config_file_path).expanduser().resolve()
        self.config: AppConfig = load_app_config(self.config_file_path)
        self.config_directory = self.config_file_path.parent
        self.path_resolver = CvPathResolver(config_directory=self.config_directory)

    # Conduz a geracao ponta a ponta e retorna o caminho absoluto do PDF produzido.
    def generate(
        self, *, language: str | None, input_file_path: str | None, output_file_path: str | None
    ) -> Path:
        # Idioma explícito em runtime tem prioridade sobre o padrão da configuração.
        effective_language = (language or self.config.defaults.language).lower()

        if input_file_path:
            data_file_path = self.path_resolver.resolve_runtime_path(input_file_path)
        else:
            data_file_path = self.path_resolver.resolve_language_aware_path(
                direct_path=self.config.files.data,
                path_by_language=self.config.files.data_by_language,
                language=effective_language,
                path_label="data",
            )

        visual_settings_path = self.path_resolver.resolve_config_relative_path(
            self.config.files.styles
        )
        translations_path = self.path_resolver.resolve_language_aware_path(
            direct_path=self.config.files.translations,
            path_by_language=self.config.files.translations_by_language,
            language=effective_language,
            path_label="translations",
        )

        started_at = time.perf_counter()
        file_encoding = self.config.defaults.encoding

        cv_data = load_json(data_file_path, encoding=file_encoding)

        if output_file_path:
            output_path = self.path_resolver.resolve_runtime_path(output_file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = self.path_resolver.build_output_file_path(
                cv_data=cv_data,
                language=effective_language,
                output_dir_config=self.config.files.output_dir,
            )

        contextual_logger = bind_logger_context(
            language=effective_language,
            input_file=str(data_file_path),
            output_file=str(output_path),
        )
        contextual_logger.bind(event="app_start", step="cv_service").debug(
            "Starting CV generation workflow"
        )

        visual_settings = load_json(visual_settings_path, encoding=file_encoding)
        translations = load_json(translations_path, encoding=file_encoding)

        validate_cv_data(cv_data)
        contextual_logger.bind(event="input_validated", step="validators").debug(
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
        self._save_used_cv_data_copy(
            data_file_path=data_file_path,
            output_directory=generated_pdf_path.parent,
        )

        elapsed_ms = int((time.perf_counter() - started_at) * 1000)
        contextual_logger.bind(
            event="app_finished",
            step="cv_service",
            duration_ms=str(elapsed_ms),
        ).info("CV generation finished")

        return generated_pdf_path

    # Copia o JSON de entrada usado na geração para a mesma pasta dos PDFs gerados.
    def _save_used_cv_data_copy(
        self,
        *,
        data_file_path: Path,
        output_directory: Path,
    ) -> None:
        copied_data_path = (output_directory / data_file_path.name).resolve()
        if copied_data_path != data_file_path.resolve():
            copy2(data_file_path, copied_data_path)


# Atalho de entrada usado por CLI/testes para executar a geracao em uma unica chamada.
def run_generation(
    *,
    config_file_path: str | Path,
    language: str | None,
    input_file_path: str | None,
    output_file_path: str | None,
) -> Path:
    service = CvGenerationService(config_file_path=config_file_path)
    # Configura logging uma única vez por processo antes de qualquer emissão de log da geração.
    logs_directory = service.path_resolver.resolve_config_relative_path(
        service.config.logging.directory
    )
    configure_logging(
        level=service.config.logging.level,
        enabled=service.config.logging.enabled,
        logs_directory=logs_directory,
    )
    generated_path = service.generate(
        language=language,
        input_file_path=input_file_path,
        output_file_path=output_file_path,
    )
    logger.bind(event="app_finished", step="entrypoint").debug(f"Generated file: {generated_path}")
    return generated_path
