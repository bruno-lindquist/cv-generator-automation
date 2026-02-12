# Este arquivo encapsula a leitura de arquivos JSON do disco.
# Ele serve para centralizar regras de acesso a JSON (encoding + tratamento de erro).
# Organização:
# - classe `JsonRepository` com configuração de encoding no construtor
# - método `load_json` para carregar e validar o conteúdo
# Entradas esperadas:
# - um `Path` apontando para arquivo JSON existente
# Saídas esperadas:
# - um dicionário Python (`dict`) com os dados do JSON
# - em caso de falha, lança exceções específicas da aplicação

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from shared.exceptions import JsonFileNotFoundError, JsonParsingError


class JsonRepository:
    # Propósito:
    # - representar um repositório simples de leitura de JSON.
    # Retorno:
    # - objetos `dict` com o conteúdo carregado.
    # Efeitos:
    # - faz leitura de arquivo no sistema de arquivos.

    # Propósito:
    # - definir o encoding usado ao abrir os arquivos JSON.
    # Retorno:
    # - None.
    # Efeitos:
    # - armazena estado interno (`self.encoding`) para leituras futuras.
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    # Propósito:
    # - carregar um arquivo JSON e devolver seu conteúdo como dicionário.
    # Retorno:
    # - `dict[str, Any]` com os dados do arquivo.
    # Efeitos:
    # - lê arquivo do disco
    # - lança exceções de domínio quando o arquivo está ausente ou inválido.
    def load_json(self, file_path: Path) -> dict[str, Any]:
        # `expanduser()` resolve `~` e `resolve()` normaliza para caminho absoluto.
        resolved_path = file_path.expanduser().resolve()

        # Falha cedo com erro explícito quando o arquivo não existe.
        if not resolved_path.exists():
            raise JsonFileNotFoundError(f"JSON file not found: {resolved_path}")

        try:
            # Abre e converte JSON em objetos Python (dict/list/str/etc.).
            with resolved_path.open("r", encoding=self.encoding) as json_file:
                data = json.load(json_file)
        except json.JSONDecodeError as exc:
            # Encapsula erro técnico do parser em erro mais semântico da aplicação.
            raise JsonParsingError(f"Invalid JSON file: {resolved_path}") from exc

        # A aplicação exige que a raiz do JSON seja um objeto (dict), não uma lista.
        if not isinstance(data, dict):
            raise JsonParsingError(f"Top-level JSON object must be a dictionary: {resolved_path}")

        return data
