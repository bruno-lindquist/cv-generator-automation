# Verifica contratos de saida da CLI para sucesso e falhas de configuracao.
from __future__ import annotations

from pathlib import Path

from cli import main
from tests.helpers.project_builders import create_test_project_files


# Monta arquivos minimos para exercitar a CLI em um ambiente temporario controlado.
def _create_valid_project_files(base_directory: Path) -> Path:
    return create_test_project_files(
        base_directory,
        cv_data={
            "personal_info": {"name": "CLI Test", "email": "cli@example.com"},
            "desired_role": {"desired_role_pt": "Desenvolvedor"},
        },
        translations={
            "pt": {
                "sections": {"summary": "Resumo"},
                "labels": {"current": "Atual"},
            }
        },
    )


# Garante o comportamento "cli main returns zero for valid generation" para evitar regressao dessa regra.
def test_cli_main_returns_zero_for_valid_generation(tmp_path: Path) -> None:
    config_path = _create_valid_project_files(tmp_path)

    exit_code = main(["-c", str(config_path), "-l", "pt"])

    assert exit_code == 0


# Garante o comportamento "cli main returns one for invalid config path" para evitar regressao dessa regra.
def test_cli_main_returns_one_for_invalid_config_path() -> None:
    exit_code = main(["-c", "missing-config-file.json"])

    assert exit_code == 1
