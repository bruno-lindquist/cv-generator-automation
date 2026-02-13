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
        "experience": ExperienceSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
        "education": EducationSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
        "core_skills": CoreSkillsSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
        "skills": SkillsSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
        "languages": LanguagesSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
        "awards": AwardsSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
        "certifications": CertificationsSectionFormatter(
            language=language,
            translations=translations,
            pdf_style_engine=pdf_style_engine,
        ),
    }
    return SectionFormatterRegistry(formatter_by_type=formatter_by_type)
