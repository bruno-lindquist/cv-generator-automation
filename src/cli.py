"""Command-line interface for the CV Generator."""

from __future__ import annotations

import argparse
from pathlib import Path

from loguru import logger

from cv_service import run_generation
from exceptions import CvGeneratorError


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    arguments = parser.parse_args(argv)

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
