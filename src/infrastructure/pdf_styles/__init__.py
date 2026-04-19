# Exporta o motor de estilos usado na renderizacao do PDF.
from infrastructure.pdf_styles.pdf_style_engine import (
    REQUIRED_PARAGRAPH_STYLE_NAMES,
    PdfStyleEngine,
)

__all__ = [
    "REQUIRED_PARAGRAPH_STYLE_NAMES",
    "PdfStyleEngine",
]
