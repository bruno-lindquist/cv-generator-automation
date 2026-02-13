# Confirma regras minimas exigidas para aceitar ou rejeitar dados de entrada.
import pytest

from validators import validate_cv_data
from exceptions import DataValidationError


# Garante o comportamento "validate cv data accepts minimal valid payload" para evitar regressao dessa regra.
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


# Garante o comportamento "validate cv data rejects missing required fields" para evitar regressao dessa regra.
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
