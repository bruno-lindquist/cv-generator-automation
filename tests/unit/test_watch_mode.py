# Exercita checksum de arquivos e o loop de observacao do modo watch.
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from watch_mode import compute_file_checksum, run_watch_mode, safe_file_checksum


# Garante o comportamento "compute file checksum matches known sha256" para evitar regressao dessa regra.
def test_compute_file_checksum_matches_known_sha256(tmp_path: Path) -> None:
    sample_file = tmp_path / "sample.txt"
    sample_bytes = b"hello world"
    sample_file.write_bytes(sample_bytes)

    expected_checksum = hashlib.sha256(sample_bytes).hexdigest()

    assert compute_file_checksum(sample_file) == expected_checksum


# Garante o comportamento "safe file checksum returns empty string for missing file" para evitar regressao dessa regra.
def test_safe_file_checksum_returns_empty_string_for_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "does-not-exist.json"

    assert safe_file_checksum(missing_file) == ""


# Garante o comportamento "safe file checksum returns valid checksum for existing file" para evitar regressao dessa regra.
def test_safe_file_checksum_returns_valid_checksum_for_existing_file(tmp_path: Path) -> None:
    existing_file = tmp_path / "existing.txt"
    existing_file.write_bytes(b"content")

    assert safe_file_checksum(existing_file) == hashlib.sha256(b"content").hexdigest()


# Garante o comportamento "safe file checksum differs when content changes" para evitar regressao dessa regra.
def test_safe_file_checksum_differs_when_content_changes(tmp_path: Path) -> None:
    mutable_file = tmp_path / "mutable.txt"
    mutable_file.write_bytes(b"first")
    first_checksum = safe_file_checksum(mutable_file)

    mutable_file.write_bytes(b"second")
    second_checksum = safe_file_checksum(mutable_file)

    assert first_checksum != second_checksum


# Garante o comportamento "run watch mode regenerates on change and stops on keyboard interrupt" para evitar regressao dessa regra.
def test_run_watch_mode_regenerates_on_change_and_stops_on_keyboard_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    watched_file = tmp_path / "input.json"
    watched_file.write_bytes(b"v1")

    run_counter = {"calls": 0}

    def fake_run_once() -> Path | None:
        run_counter["calls"] += 1
        return None

    sleep_counter = {"calls": 0}

    def fake_sleep(_seconds: float) -> None:
        sleep_counter["calls"] += 1
        # Primeira iteracao: altera o arquivo para forcar regeneracao.
        if sleep_counter["calls"] == 1:
            watched_file.write_bytes(b"v2")
            return
        # Segunda iteracao: encerra o loop simulando Ctrl+C.
        raise KeyboardInterrupt

    monkeypatch.setattr("watch_mode.time.sleep", fake_sleep)

    run_watch_mode(
        watched_files=[watched_file],
        run_once=fake_run_once,
        poll_interval_seconds=0.0,
        open_viewer=False,
    )

    # Uma geracao inicial + uma regeneracao apos detectar mudanca.
    assert run_counter["calls"] == 2
