"""PDF rendering infrastructure for CV generation."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
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
    REQUIRED_PARAGRAPH_STYLE_NAMES = [
        "NameStyle",
        "TitleStyle",
        "SectionTitleStyle",
        "ItemTitleStyle",
        "ItemSubtitleStyle",
        "BodyStyle",
        "ContactStyle",
        "DateStyle",
    ]
    STYLE_FIELD_MAPPING = {
        "font_name": "fontName",
        "font_size": "fontSize",
        "text_color": "textColor",
        "space_before": "spaceBefore",
        "space_after": "spaceAfter",
        "left_indent": "leftIndent",
        "alignment": "alignment",
        "keep_with_next": "keepWithNext",
    }
    ALIGNMENT_BY_NAME = {
        "left": TA_LEFT,
        "center": TA_CENTER,
        "right": TA_RIGHT,
        "justify": TA_JUSTIFY,
    }

    def __init__(
        self,
        *,
        language: str,
        translations: dict[str, Any],
        visual_settings: dict[str, Any],
    ) -> None:
        self.language = language
        self.translations = translations
        self.visual_settings = visual_settings if isinstance(visual_settings, dict) else {}
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
            rightMargin=self._margin("right") * mm,
            leftMargin=self._margin("left") * mm,
            topMargin=self._margin("top") * mm,
            bottomMargin=self._margin("bottom") * mm,
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
            elements.append(Spacer(1, self._spacing("item_bottom") * mm))

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
        paragraph_styles = self.visual_settings.get("paragraph_styles", {})
        if not isinstance(paragraph_styles, dict):
            raise PdfRenderError(
                "Style configuration missing 'paragraph_styles' dictionary in styles.json"
            )

        for style_name, style_definition in paragraph_styles.items():
            if not isinstance(style_name, str) or not isinstance(style_definition, dict):
                continue
            if style_name in styles.byName:
                continue

            parent_name = str(style_definition.get("parent", "Normal"))
            parent_style = styles[parent_name] if parent_name in styles else styles["Normal"]
            style_kwargs = self._build_paragraph_style_kwargs(style_definition)
            styles.add(ParagraphStyle(name=style_name, parent=parent_style, **style_kwargs))

        missing_required_styles = [
            style_name
            for style_name in self.REQUIRED_PARAGRAPH_STYLE_NAMES
            if style_name not in styles.byName
        ]
        if missing_required_styles:
            missing_styles = ", ".join(missing_required_styles)
            raise PdfRenderError(
                f"Style configuration missing required paragraph styles: {missing_styles}"
            )

        return styles

    def _build_paragraph_style_kwargs(self, style_definition: dict[str, Any]) -> dict[str, Any]:
        style_kwargs: dict[str, Any] = {}
        for setting_key, reportlab_key in self.STYLE_FIELD_MAPPING.items():
            if setting_key not in style_definition:
                continue

            setting_value = style_definition[setting_key]
            if setting_key == "alignment":
                style_kwargs[reportlab_key] = self._resolve_alignment(setting_value)
                continue
            if setting_key == "text_color":
                style_kwargs[reportlab_key] = self._resolve_color(setting_value)
                continue

            style_kwargs[reportlab_key] = setting_value

        return style_kwargs

    def _resolve_alignment(self, alignment_value: Any) -> int:
        if isinstance(alignment_value, int):
            return alignment_value
        if not isinstance(alignment_value, str):
            return TA_LEFT
        return self.ALIGNMENT_BY_NAME.get(alignment_value.lower(), TA_LEFT)

    def _resolve_color(self, color_value: Any) -> colors.Color:
        if not isinstance(color_value, str) or not color_value.strip():
            raise PdfRenderError("Paragraph style 'text_color' must be a non-empty string")
        try:
            return colors.toColor(color_value)
        except ValueError:
            raise PdfRenderError(f"Invalid paragraph style color: {color_value}")

    def _link_color(self) -> str:
        links_settings = self.visual_settings.get("links", {})
        if not isinstance(links_settings, dict):
            raise PdfRenderError(
                "Style configuration missing 'links' dictionary in styles.json"
            )
        link_color = links_settings.get("social_link_color")
        if not isinstance(link_color, str) or not link_color.strip():
            raise PdfRenderError(
                "Style configuration missing 'links.social_link_color' in styles.json"
            )
        return link_color

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
            escaped_link_color = escape(self._link_color(), {"'": "&apos;", '"': "&quot;"})
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
                social_links.append(
                    f'<a href="{escaped_url}" color="{escaped_link_color}">{escaped_label}</a>'
                )

            if social_links:
                elements.append(Paragraph(" | ".join(social_links), styles["ContactStyle"]))

        elements.append(Spacer(1, self._spacing("header_bottom") * mm))

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
        elements.append(Spacer(1, self._spacing("section_bottom") * mm))

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

        elements.append(Spacer(1, self._spacing("small_bottom") * mm))

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

        elements.append(Spacer(1, self._spacing("small_bottom") * mm))

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

        elements.append(Spacer(1, self._spacing("minimal_bottom") * mm))

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

        elements.append(Spacer(1, self._spacing("item_bottom") * mm))

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

    def _margin(self, margin_key: str) -> float:
        margin_settings = self.visual_settings.get("margins", {})
        if not isinstance(margin_settings, dict):
            raise PdfRenderError("Style configuration missing 'margins' dictionary in styles.json")
        margin_value = margin_settings.get(margin_key)
        if margin_value is None:
            raise PdfRenderError(
                f"Style configuration missing 'margins.{margin_key}' in styles.json"
            )
        return float(margin_value)

    def _spacing(self, spacing_key: str) -> float:
        spacing_settings = self.visual_settings.get("spacing", {})
        if not isinstance(spacing_settings, dict):
            raise PdfRenderError("Style configuration missing 'spacing' dictionary in styles.json")
        spacing_value = spacing_settings.get(spacing_key)
        if spacing_value is None:
            raise PdfRenderError(
                f"Style configuration missing 'spacing.{spacing_key}' in styles.json"
            )
        return float(spacing_value)
