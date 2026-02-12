"""Validation rules for CV input data."""

from __future__ import annotations

from typing import Any

from shared.exceptions import DataValidationError


REQUIRED_TOP_LEVEL_FIELDS = ["personal_info", "desired_role"]
REQUIRED_PERSONAL_INFO_FIELDS = ["name", "email"]


def validate_cv_data(cv_data: dict[str, Any]) -> None:
    """Validate required data schema for CV generation."""
    validation_errors: list[str] = []

    for required_field in REQUIRED_TOP_LEVEL_FIELDS:
        if required_field not in cv_data:
            validation_errors.append(f"Missing top-level field: '{required_field}'")

    personal_info = cv_data.get("personal_info", {})
    if isinstance(personal_info, dict):
        for required_personal_field in REQUIRED_PERSONAL_INFO_FIELDS:
            if not personal_info.get(required_personal_field):
                validation_errors.append(
                    f"Missing required field: 'personal_info.{required_personal_field}'"
                )
    else:
        validation_errors.append("Field 'personal_info' must be a dictionary")

    desired_role = cv_data.get("desired_role", {})
    if not isinstance(desired_role, dict):
        validation_errors.append("Field 'desired_role' must be a dictionary")

    if validation_errors:
        error_message = "Invalid cv_data.json:\n- " + "\n- ".join(validation_errors)
        raise DataValidationError(error_message, validation_errors)
