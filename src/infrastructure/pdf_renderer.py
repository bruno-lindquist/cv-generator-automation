"""PDF rendering infrastructure for CV generation."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from domain.localization import (
    escape_text_preserving_tags,
    format_period,
    get_localized_field,
    get_localized_list,
    get_translation,
    process_rich_text,
)
from shared.exceptions import PdfRenderError


class CvPdfRenderer:
    """Render CV data into a PDF document."""

    DEFAULT_SECTION_ORDER = [
        "experience",
        "education",
        "core_skills",
        "skills",
        "languages",
        "awards",
        "certifications",
    ]

    def __init__(
        self,
        *,
        language: str,
        translations: dict[str, Any],
        visual_settings: dict[str, Any],
    ) -> None:
        self.language = language
        self.translations = translations
        self.visual_settings = visual_settings
        self.section_formatter_by_type = {
            "experience": self._format_experience_item,
            "education": self._format_education_item,
            "core_skills": self._format_core_skills_item,
            "skills": self._format_skills_item,
            "languages": self._format_language_item,
            "awards": self._format_award_item,
            "certifications": self._format_certification_item,
        }

    def render_cv(
        self,
        *,
        cv_data: dict[str, Any],
        output_file_path: Path,
        app_logger: Any,
    ) -> Path:
        """Render and persist a PDF file from CV input data."""
        output_file_path.parent.mkdir(parents=True, exist_ok=True)

        document = SimpleDocTemplate(
            str(output_file_path),
            pagesize=A4,
            rightMargin=self._margin("right", 19) * mm,
            leftMargin=self._margin("left", 19) * mm,
            topMargin=self._margin("top", 19) * mm,
            bottomMargin=self._margin("bottom", 19) * mm,
        )

        app_logger.bind(event="pdf_build_started", step="pdf_renderer").info(
            "Building PDF document"
        )

        elements: list[Any] = []
        styles = self._create_styles()

        self._add_header(elements, styles, cv_data)
        self._add_summary(elements, styles, cv_data)
        self._add_dynamic_sections(elements, styles, cv_data, app_logger)

        try:
            document.build(elements)
        except Exception as exc:  # pragma: no cover - external library behavior
            raise PdfRenderError(f"Failed to build PDF: {output_file_path}") from exc

        app_logger.bind(event="pdf_build_finished", step="pdf_renderer").info(
            "PDF document built successfully"
        )
        return output_file_path

    def _add_dynamic_sections(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        cv_data: dict[str, Any],
        app_logger: Any,
    ) -> None:
        for section_type in self._resolve_sections_to_render(cv_data):
            section_items = cv_data.get(section_type, [])
            if not section_items:
                continue

            if not isinstance(section_items, list):
                app_logger.bind(
                    event="section_render_skipped",
                    step=section_type,
                ).warning("Section data is not a list; skipping section")
                continue

            formatter = self.section_formatter_by_type.get(section_type)
            if not formatter:
                app_logger.bind(event="section_render_skipped", step=section_type).warning(
                    "Unknown section type; skipping section"
                )
                continue

            section_start = time.perf_counter()
            app_logger.bind(event="section_render_started", step=section_type).info(
                "Rendering section"
            )

            self._add_section_title(elements, styles, section_type)
            for item in section_items:
                formatter(elements, styles, item)
            elements.append(Spacer(1, self._spacing("item_bottom", 1) * mm))

            elapsed_ms = int((time.perf_counter() - section_start) * 1000)
            app_logger.bind(
                event="section_render_finished",
                step=section_type,
                duration_ms=str(elapsed_ms),
            ).info("Finished rendering section")

    def _resolve_sections_to_render(self, cv_data: dict[str, Any]) -> list[str]:
        sections_config = cv_data.get("sections")
        if not isinstance(sections_config, list):
            return self.DEFAULT_SECTION_ORDER

        enabled_sections = [
            section
            for section in sections_config
            if isinstance(section, dict) and section.get("enabled", True)
        ]
        sorted_sections = sorted(enabled_sections, key=lambda section: section.get("order", 999))

        section_types: list[str] = []
        for section in sorted_sections:
            section_type = section.get("type")
            if isinstance(section_type, str) and section_type and section_type not in section_types:
                section_types.append(section_type)

        return section_types

    def _create_styles(self) -> StyleSheet1:
        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="NameStyle",
                parent=styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#000000"),
                spaceAfter=6,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )
        styles.add(
            ParagraphStyle(
                name="TitleStyle",
                parent=styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#000000"),
                spaceAfter=24,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )
        styles.add(
            ParagraphStyle(
                name="SectionTitleStyle",
                parent=styles["Normal"],
                fontSize=14,
                textColor=colors.HexColor("#888888"),
                spaceBefore=14,
                spaceAfter=6,
                fontName="Helvetica-Bold",
                keepWithNext=1,
            )
        )
        styles.add(
            ParagraphStyle(
                name="ItemTitleStyle",
                parent=styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#000000"),
                spaceBefore=10,
                spaceAfter=4,
                leftIndent=10,
                fontName="Helvetica-Bold",
                keepWithNext=1,
            )
        )
        styles.add(
            ParagraphStyle(
                name="ItemSubtitleStyle",
                parent=styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor("#000000"),
                spaceAfter=2,
                leftIndent=10,
                fontName="Helvetica-Bold",
                keepWithNext=1,
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodyStyle",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#000000"),
                spaceAfter=2,
                leftIndent=28,
                alignment=TA_JUSTIFY,
                fontName="Helvetica",
            )
        )
        styles.add(
            ParagraphStyle(
                name="ContactStyle",
                parent=styles["BodyStyle"],
                fontSize=11,
                alignment=TA_CENTER,
                leftIndent=0,
                fontName="Helvetica",
            )
        )
        styles.add(
            ParagraphStyle(
                name="DateStyle",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor("#000000"),
                leftIndent=10,
                spaceAfter=2,
                fontName="Helvetica",
            )
        )

        return styles

    def _add_header(self, elements: list[Any], styles: StyleSheet1, cv_data: dict[str, Any]) -> None:
        personal_info = cv_data.get("personal_info", {})

        name = personal_info.get("name", "")
        if name:
            elements.append(Paragraph(escape_text_preserving_tags(name), styles["NameStyle"]))

        desired_role = get_localized_field(
            cv_data.get("desired_role", {}),
            "desired_role",
            self.language,
            "",
        )
        if desired_role:
            elements.append(Paragraph(escape_text_preserving_tags(desired_role), styles["TitleStyle"]))

        contact_items: list[str] = []
        phone_number = str(personal_info.get("phone", "")).strip()
        if phone_number:
            if self.language == "en" and not phone_number.startswith("+55"):
                phone_number = f"+55 {phone_number}"
            contact_items.append(phone_number)

        email = str(personal_info.get("email", "")).strip()
        if email:
            contact_items.append(email)

        location = str(personal_info.get("location", "")).strip()
        if location:
            contact_items.append(location)

        if contact_items:
            contact_text = " | ".join(contact_items)
            elements.append(Paragraph(escape_text_preserving_tags(contact_text), styles["ContactStyle"]))

        social_items = personal_info.get("social") or []
        if isinstance(social_items, list) and social_items:
            social_links: list[str] = []
            for social_item in social_items:
                if not isinstance(social_item, dict):
                    continue
                label = str(social_item.get("label", "")).strip()
                url = str(social_item.get("url", "")).strip()
                if not url:
                    continue

                escaped_url = escape(url, {"'": "&apos;", '"': "&quot;"})
                label_text = label or url
                escaped_label = escape_text_preserving_tags(label_text)
                social_links.append(f'<a href="{escaped_url}" color="blue">{escaped_label}</a>')

            if social_links:
                elements.append(Paragraph(" | ".join(social_links), styles["ContactStyle"]))

        elements.append(Spacer(1, self._spacing("header_bottom", 0) * mm))

    def _add_summary(self, elements: list[Any], styles: StyleSheet1, cv_data: dict[str, Any]) -> None:
        summary = get_localized_field(cv_data.get("summary", {}), "description", self.language, "")
        if not summary:
            return

        section_title = get_translation(
            self.translations,
            self.language,
            "sections",
            "summary",
            "Summary",
        )
        elements.append(Paragraph(escape_text_preserving_tags(section_title), styles["SectionTitleStyle"]))
        elements.append(Paragraph(process_rich_text(summary), styles["BodyStyle"]))
        elements.append(Spacer(1, self._spacing("section_bottom", 2) * mm))

    def _add_section_title(self, elements: list[Any], styles: StyleSheet1, section_type: str) -> None:
        section_title = get_translation(
            self.translations,
            self.language,
            "sections",
            section_type,
            section_type,
        )
        elements.append(
            Paragraph(escape_text_preserving_tags(section_title), styles["SectionTitleStyle"])
        )

    def _format_experience_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        experience_item: dict[str, Any],
    ) -> None:
        position = get_localized_field(experience_item, "position", self.language, "")
        company = get_localized_field(experience_item, "company", self.language, "")
        period_text = format_period(
            start_month=experience_item.get("start_month", ""),
            start_year=experience_item.get("start_year", ""),
            end_month=experience_item.get("end_month", ""),
            end_year=experience_item.get("end_year", ""),
            translations=self.translations,
            language=self.language,
        )

        if position:
            elements.append(
                Paragraph(f"<b>{escape_text_preserving_tags(position)}</b>", styles["ItemTitleStyle"])
            )
        if company:
            elements.append(
                Paragraph(f"<b>{escape_text_preserving_tags(company)}</b>", styles["ItemSubtitleStyle"])
            )
        if period_text:
            elements.append(
                Paragraph(f"<i>{escape_text_preserving_tags(period_text)}</i>", styles["DateStyle"])
            )

        descriptions = self._localized_list(experience_item, "description")
        for description in descriptions:
            elements.append(Paragraph(f"• {process_rich_text(description)}", styles["BodyStyle"]))

        elements.append(Spacer(1, self._spacing("small_bottom", 1) * mm))

    def _format_education_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        education_item: dict[str, Any],
    ) -> None:
        degree = get_localized_field(education_item, "degree", self.language, "")
        institution = get_localized_field(education_item, "institution", self.language, "")
        period_text = format_period(
            start_month=education_item.get("start_month", ""),
            start_year=education_item.get("start_year", ""),
            end_month=education_item.get("end_month", ""),
            end_year=education_item.get("end_year", ""),
            translations=self.translations,
            language=self.language,
        )

        if degree:
            elements.append(
                Paragraph(f"<b>{escape_text_preserving_tags(degree)}</b>", styles["ItemTitleStyle"])
            )
        if institution:
            elements.append(
                Paragraph(
                    f"<b>{escape_text_preserving_tags(institution)}</b>",
                    styles["ItemSubtitleStyle"],
                )
            )
        if period_text:
            elements.append(
                Paragraph(f"<i>{escape_text_preserving_tags(period_text)}</i>", styles["DateStyle"])
            )

        descriptions = self._localized_list(education_item, "description")
        for description in descriptions:
            elements.append(Paragraph(f"• {process_rich_text(description)}", styles["BodyStyle"]))

        elements.append(Spacer(1, self._spacing("small_bottom", 1) * mm))

    def _format_core_skills_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        core_skill_item: dict[str, Any],
    ) -> None:
        category = get_localized_field(core_skill_item, "category", self.language, "")
        if category:
            elements.append(Paragraph(escape_text_preserving_tags(category), styles["ItemTitleStyle"]))

        descriptions = self._localized_list(core_skill_item, "description")
        for description in descriptions:
            elements.append(Paragraph(f"• {process_rich_text(description)}", styles["BodyStyle"]))

        elements.append(Spacer(1, self._spacing("minimal_bottom", 0.1) * mm))

    def _format_skills_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        skill_group_item: dict[str, Any],
    ) -> None:
        category = get_localized_field(skill_group_item, "category", self.language, "")
        if category:
            elements.append(Paragraph(escape_text_preserving_tags(category), styles["ItemTitleStyle"]))

        skills = skill_group_item.get("item", [])
        if isinstance(skills, list) and skills:
            safe_skills = ", ".join(escape_text_preserving_tags(skill) for skill in skills)
            elements.append(Paragraph(safe_skills, styles["BodyStyle"]))

        elements.append(Spacer(1, self._spacing("item_bottom", 1) * mm))

    def _format_language_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        language_item: dict[str, Any],
    ) -> None:
        language_name = get_localized_field(language_item, "language", self.language, "")
        proficiency = get_localized_field(language_item, "proficiency", self.language, "")
        if language_name or proficiency:
            body_text = (
                f"<b>{escape_text_preserving_tags(language_name)}</b> - "
                f"{escape_text_preserving_tags(proficiency)}"
            )
            elements.append(Paragraph(body_text, styles["BodyStyle"]))

    def _format_award_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        award_item: dict[str, Any],
    ) -> None:
        title = get_localized_field(award_item, "title", self.language, "")
        description = get_localized_field(award_item, "description", self.language, "")

        if title and description:
            award_text = (
                f"<b>{escape_text_preserving_tags(title)}</b> - "
                f"{escape_text_preserving_tags(description)}"
            )
        else:
            award_text = escape_text_preserving_tags(title or description)

        if award_text:
            elements.append(Paragraph(award_text, styles["BodyStyle"]))

    def _format_certification_item(
        self,
        elements: list[Any],
        styles: StyleSheet1,
        certification_item: dict[str, Any],
    ) -> None:
        certification_name = get_localized_field(certification_item, "name", self.language, "")
        issuer_name = get_localized_field(certification_item, "issuer", self.language, "")
        year = str(certification_item.get("year", "")).strip()

        if certification_name and issuer_name and year:
            certification_text = (
                f"<b>{escape_text_preserving_tags(certification_name)}</b> - "
                f"{escape_text_preserving_tags(issuer_name)} "
                f"({escape_text_preserving_tags(year)})"
            )
        elif certification_name and issuer_name:
            certification_text = (
                f"<b>{escape_text_preserving_tags(certification_name)}</b> - "
                f"{escape_text_preserving_tags(issuer_name)}"
            )
        else:
            certification_text = escape_text_preserving_tags(certification_name or issuer_name)

        if certification_text:
            elements.append(Paragraph(certification_text, styles["BodyStyle"]))

    def _localized_list(self, entry: dict[str, Any], field_name: str) -> list[str]:
        return get_localized_list(entry, field_name, self.language)

    def _margin(self, margin_key: str, default_value: float) -> float:
        margin_settings = self.visual_settings.get("margins", {})
        if not isinstance(margin_settings, dict):
            return default_value
        margin_value = margin_settings.get(margin_key, default_value)
        return float(margin_value)

    def _spacing(self, spacing_key: str, default_value: float) -> float:
        spacing_settings = self.visual_settings.get("spacing", {})
        if not isinstance(spacing_settings, dict):
            return default_value
        spacing_value = spacing_settings.get(spacing_key, default_value)
        return float(spacing_value)
