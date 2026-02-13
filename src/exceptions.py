# Hierarquia de excecoes de dominio para diferenciar falhas esperadas de erros genericos.
from __future__ import annotations


# Base para erros controlados da aplicacao, facilitando tratamento centralizado na CLI.
class CvGeneratorError(Exception):
    # Mantem uma base comum para os erros do projeto.
    pass


# Usada quando config.json esta ausente, invalido ou incompleto.
class ConfigurationError(CvGeneratorError):
    # Identifica erros de configuracao da aplicacao.
    pass


# Sinaliza ausencia de arquivo JSON esperado durante a execucao.
class JsonFileNotFoundError(CvGeneratorError):
    # Sinaliza ausencia de um arquivo JSON esperado.
    pass


# Indica JSON malformado ou com estrutura raiz inesperada.
class JsonParsingError(CvGeneratorError):
    # Indica falha ao interpretar o conteudo JSON.
    pass


# Representa falhas de schema no payload de curriculo, com lista detalhada de erros.
class DataValidationError(CvGeneratorError):

    # Guarda a lista de validacoes quebradas para exibicao amigavel e asserts de teste.
    def __init__(self, message: str, validation_errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.validation_errors = validation_errors or []


# Protege contra caminhos de saida invalidos ou potencialmente inseguros.
class OutputPathError(CvGeneratorError):
    # Sinaliza problemas ao gerar o caminho de saida.
    pass


# Encapsula falhas ocorridas durante montagem e escrita do PDF.
class PdfRenderError(CvGeneratorError):
    # Indica falhas no processo de renderizacao do PDF.
    pass
