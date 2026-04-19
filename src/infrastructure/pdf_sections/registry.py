# Registro que mapeia cada tipo de secao para o formatador responsavel.
from __future__ import annotations

from typing import Any

from infrastructure.pdf_sections.base import BaseSectionFormatter
from infrastructure.pdf_sections.simple import (
    AwardsSectionFormatter,
    CertificationsSectionFormatter,
    CoreSkillsSectionFormatter,
    LanguagesSectionFormatter,
    SkillsSectionFormatter,
)
from infrastructure.pdf_sections.timeline import (
    EducationSectionFormatter,
    ExperienceSectionFormatter,
)
from infrastructure.pdf_styles import PdfStyleEngine

# Tipo de secao -> classe concreta do formatador responsavel.
_FORMATTER_CLASS_BY_TYPE: dict[str, type[BaseSectionFormatter]] = {
    "experience": ExperienceSectionFormatter,
    "education": EducationSectionFormatter,
    "core_skills": CoreSkillsSectionFormatter,
    "skills": SkillsSectionFormatter,
    "languages": LanguagesSectionFormatter,
    "awards": AwardsSectionFormatter,
    "certifications": CertificationsSectionFormatter,
}


# Encapsula o lookup de formatadores para desacoplar renderizador de classes concretas.
class SectionFormatterRegistry:
    # Recebe o mapa de formatadores ja prontos para consulta por tipo de secao.
    def __init__(self, formatter_by_type: dict[str, BaseSectionFormatter]) -> None:
        self._formatter_by_type = formatter_by_type

    # Retorna formatador da secao ou None para permitir skip controlado de tipos desconhecidos.
    def get_formatter(self, section_type: str) -> BaseSectionFormatter | None:
        return self._formatter_by_type.get(section_type)


# Monta o registro padrao com todos os formatadores suportados pelo projeto.
def build_default_section_formatter_registry(
    *,
    language: str,
    translations: dict[str, Any],
    pdf_style_engine: PdfStyleEngine,
) -> SectionFormatterRegistry:
    # Cada formatador recebe o mesmo contexto para manter consistência visual/idioma.
    formatter_by_type = {
        section_type: formatter_class(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        )
        for section_type, formatter_class in _FORMATTER_CLASS_BY_TYPE.items()
    }
    return SectionFormatterRegistry(formatter_by_type=formatter_by_type)
