"""Custom exceptions used by the CV Generator application."""

from __future__ import annotations


class CvGeneratorError(Exception):
    """Base exception for all domain/application errors."""


class ConfigurationError(CvGeneratorError):
    """Raised when configuration is missing or invalid."""


class JsonFileNotFoundError(CvGeneratorError):
    """Raised when a JSON file cannot be found."""


class JsonParsingError(CvGeneratorError):
    """Raised when JSON content cannot be parsed."""


class DataValidationError(CvGeneratorError):
    """Raised when CV input data does not match required schema."""

    def __init__(self, message: str, validation_errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.validation_errors = validation_errors or []


class OutputPathError(CvGeneratorError):
    """Raised when output path cannot be generated safely."""


class PdfRenderError(CvGeneratorError):
    """Raised when PDF rendering fails."""
