"""Logging configuration helpers based on Loguru."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from loguru import logger

DEFAULT_LOG_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {extra[event]} | "
    "request_id={extra[request_id]} | language={extra[language]} | "
    "step={extra[step]} | {message}"
)

DEFAULT_LOG_EXTRA = {
    "event": "-",
    "request_id": "-",
    "language": "-",
    "input_file": "-",
    "output_file": "-",
    "step": "-",
    "duration_ms": "-",
}


def configure_logging(*, level: str = "INFO", enabled: bool = True, logs_directory: Path) -> None:
    """Configure console and file sinks for Loguru."""
    logs_directory.mkdir(parents=True, exist_ok=True)

    effective_level = level.upper() if enabled else "WARNING"

    logger.remove()
    logger.configure(extra=DEFAULT_LOG_EXTRA)

    logger.add(
        sys.stderr,
        level=effective_level,
        format=DEFAULT_LOG_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=False,
    )
    logger.add(
        logs_directory / "cv_generator.log",
        level=effective_level,
        format=DEFAULT_LOG_FORMAT,
        rotation="5 MB",
        retention="14 days",
        backtrace=True,
        diagnose=False,
    )


def bind_logger_context(
    *,
    request_id: str,
    language: str,
    input_file: str,
    output_file: str,
) -> Any:
    """Return a contextualized logger instance."""
    return logger.bind(
        request_id=request_id,
        language=language,
        input_file=input_file,
        output_file=output_file,
    )
