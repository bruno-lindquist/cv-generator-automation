import pytest

from domain.validators import validate_cv_data
from shared.exceptions import DataValidationError


def test_validate_cv_data_accepts_minimal_valid_payload() -> None:
    valid_payload = {
        "personal_info": {
            "name": "Maria Tester",
            "email": "maria@example.com",
        },
        "desired_role": {
            "desired_role_pt": "Desenvolvedora",
        },
    }

    validate_cv_data(valid_payload)


def test_validate_cv_data_rejects_missing_required_fields() -> None:
    invalid_payload = {
        "personal_info": {
            "name": "Maria Tester",
        }
    }

    with pytest.raises(DataValidationError) as raised_error:
        validate_cv_data(invalid_payload)

    assert "desired_role" in str(raised_error.value)
    assert "personal_info.email" in str(raised_error.value)
