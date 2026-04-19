# Modo de observação que regenera o PDF sempre que o arquivo de entrada muda.
from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

from loguru import logger


# Calcula checksum SHA-256 de um arquivo para detectar mudancas reais de conteudo.
def compute_file_checksum(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


# Checksum resiliente a arquivos ausentes — retorna string vazia quando nao existe.
def safe_file_checksum(file_path: Path) -> str:
    if not file_path.exists():
        return ""
    return compute_file_checksum(file_path)


# Abre um arquivo ou pasta usando o aplicativo padrao do sistema operacional.
def open_with_system_viewer(path: Path) -> None:
    if sys.platform == "darwin":
        # -a Finder garante que a janela do Finder venha ao primeiro plano mesmo se ja estiver aberta.
        target = ["-a", "Finder", str(path)] if path.is_dir() else [str(path)]
        subprocess.run(["open", *target], check=False)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", str(path)], check=False)
    elif sys.platform == "win32":
        subprocess.run(["explorer", str(path)], check=False, shell=False)


# Loop principal do modo watch: gera uma vez e depois observa arquivos por mudancas.
def run_watch_mode(
    *,
    watched_files: list[Path],
    run_once: Callable[[], Path | None],
    poll_interval_seconds: float = 1.0,
    open_viewer: bool = False,
) -> None:
    last_checksums: dict[Path, str] = {
        file_path: safe_file_checksum(file_path) for file_path in watched_files
    }
    first_output = run_once()
    if first_output and open_viewer:
        open_with_system_viewer(first_output.parent)

    logger.bind(event="watch_started", step="watch").info(
        f"Watching {len(watched_files)} file(s). Press Ctrl+C to stop."
    )
    try:
        while True:
            time.sleep(poll_interval_seconds)
            changed_files = [
                file_path
                for file_path in watched_files
                if safe_file_checksum(file_path) != last_checksums.get(file_path, "")
            ]
            if not changed_files:
                continue

            logger.bind(event="watch_change", step="watch").info(
                f"Changed: {', '.join(str(file) for file in changed_files)}"
            )
            try:
                output_path = run_once()
            except Exception as generation_error:
                logger.bind(event="watch_error", step="watch").error(
                    f"Regeneration failed: {generation_error}"
                )
                # Atualiza checksums mesmo em falha para evitar loop infinito sobre mesmo conteudo.
                for file_path in changed_files:
                    last_checksums[file_path] = safe_file_checksum(file_path)
                continue

            for file_path in changed_files:
                last_checksums[file_path] = safe_file_checksum(file_path)
            if output_path and open_viewer:
                open_with_system_viewer(output_path.parent)
    except KeyboardInterrupt:
        logger.bind(event="watch_stopped", step="watch").info("Watch mode stopped by user.")
