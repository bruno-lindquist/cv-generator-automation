# Entrada de linha de comando que transforma argumentos do usuario em uma execucao segura do gerador.
from __future__ import annotations

import argparse
from pathlib import Path

from loguru import logger

from cv_service import CvGenerationService, run_generation
from exceptions import CvGeneratorError
from watch_mode import open_with_system_viewer, run_watch_mode


# Monta o parser da CLI com defaults do projeto e validacao de opcoes aceitas.
def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate CV in PDF from JSON file (with multilingual support)",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="JSON file with CV data (default defined in config file)",
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=["pt", "en"],
        default=None,
        help="CV language: pt (Portuguese) or en (English)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output PDF file",
    )
    parser.add_argument(
        "-c",
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "config" / "config.json"),
        help="Configuration file (default: config/config.json in project root)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Regenerate the PDF whenever the input JSON or configured translations/styles change",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the folder containing the generated PDF in the system's file manager",
    )
    return parser


# Descobre o arquivo de entrada que sera observado no modo watch a partir dos argumentos e config.
def _resolve_watch_input_path(arguments: argparse.Namespace) -> Path:
    if arguments.input:
        return Path(arguments.input).expanduser().resolve()
    service_for_paths = CvGenerationService(config_file_path=arguments.config)
    effective_language = (arguments.language or service_for_paths.config.defaults.language).lower()
    return service_for_paths.path_resolver.resolve_language_aware_path(
        direct_path=service_for_paths.config.files.data,
        path_by_language=service_for_paths.config.files.data_by_language,
        language=effective_language,
        path_label="data",
    )


# Executa o modo watch: primeira geracao e depois observa o JSON por mudancas.
def _run_watch(arguments: argparse.Namespace) -> int:
    try:
        input_path = _resolve_watch_input_path(arguments)
    except CvGeneratorError as resolution_error:
        logger.bind(event="app_failed", step="cli").error(str(resolution_error))
        print(f"Error: {resolution_error}")
        return 1

    def run_once() -> Path | None:
        try:
            return run_generation(
                config_file_path=arguments.config,
                language=arguments.language,
                input_file_path=arguments.input,
                output_file_path=arguments.output,
            )
        except CvGeneratorError as generation_error:
            logger.bind(event="watch_error", step="cli").error(str(generation_error))
            return None

    run_watch_mode(
        watched_files=[input_path],
        run_once=run_once,
        open_viewer=arguments.open,
    )
    return 0


# Conduz o fluxo da CLI, convertendo excecoes em codigo de saida adequado para shell/CI.
def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    arguments = parser.parse_args(argv)

    if arguments.watch:
        return _run_watch(arguments)

    try:
        generated_file = run_generation(
            config_file_path=arguments.config,
            language=arguments.language,
            input_file_path=arguments.input,
            output_file_path=arguments.output,
        )
    except CvGeneratorError as generation_error:
        logger.bind(event="app_failed", step="cli").error(str(generation_error))
        print(f"Error: {generation_error}")
        return 1
    except Exception:
        logger.bind(event="app_failed", step="cli").critical(
            "Unexpected fatal error while running CLI"
        )
        logger.exception("Unhandled exception in CLI")
        return 1

    print(f"✓ CV generated successfully: {generated_file}")
    if arguments.open:
        open_with_system_viewer(generated_file.parent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
