"""Registry for mapping section types to section formatters."""

from __future__ import annotations

from typing import Any

from infrastructure.pdf_sections.awards_section_formatter import AwardsSectionFormatter
from infrastructure.pdf_sections.base_section_formatter import BaseSectionFormatter
from infrastructure.pdf_sections.certifications_section_formatter import (
    CertificationsSectionFormatter,
)
from infrastructure.pdf_sections.core_skills_section_formatter import (
    CoreSkillsSectionFormatter,
)
from infrastructure.pdf_sections.education_section_formatter import (
    EducationSectionFormatter,
)
from infrastructure.pdf_sections.experience_section_formatter import (
    ExperienceSectionFormatter,
)
from infrastructure.pdf_sections.languages_section_formatter import (
    LanguagesSectionFormatter,
)
from infrastructure.pdf_sections.skills_section_formatter import SkillsSectionFormatter
from infrastructure.pdf_styles import PdfStyleEngine


class SectionFormatterRegistry:
    """Central registry for section formatter lookup."""

    def __init__(self, formatter_by_type: dict[str, BaseSectionFormatter]) -> None:
        self._formatter_by_type = formatter_by_type

    def get_formatter(self, section_type: str) -> BaseSectionFormatter | None:
        """Return formatter for section type, or None when not registered."""
        return self._formatter_by_type.get(section_type)


def build_default_section_formatter_registry(
    *,
    language: str,
    translations: dict[str, Any],
    pdf_style_engine: PdfStyleEngine,
) -> SectionFormatterRegistry:
    """Build the default project registry with all supported section formatters."""
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
