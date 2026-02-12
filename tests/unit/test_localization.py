from cv_generator_app.domain.localization import (
    escape_text_preserving_tags,
    format_period,
    get_localized_field,
    sanitize_filename_component,
)


def test_get_localized_field_prefers_target_language() -> None:
    field_data = {
        "position_pt": "Desenvolvedor",
        "position_en": "Developer",
    }

    assert get_localized_field(field_data, "position", "en") == "Developer"


def test_get_localized_field_falls_back_to_portuguese() -> None:
    field_data = {
        "position_pt": "Desenvolvedor",
        "position": "Generic",
    }

    assert get_localized_field(field_data, "position", "en") == "Desenvolvedor"


def test_escape_text_preserves_supported_tags() -> None:
    raw_text = "<b>Hello</b> & <i>world</i>"
    escaped_text = escape_text_preserving_tags(raw_text)

    assert "<b>Hello</b>" in escaped_text
    assert "<i>world</i>" in escaped_text
    assert "&amp;" in escaped_text


def test_format_period_uses_present_label_when_missing_end_date() -> None:
    translations = {
        "en": {
            "labels": {
                "current": "Present",
            }
        }
    }

    period_text = format_period(
        start_month="1",
        start_year="2022",
        end_month="",
        end_year="",
        translations=translations,
        language="en",
    )

    assert period_text == "Jan 2022 - Present"


def test_sanitize_filename_component_removes_unsafe_characters() -> None:
    sanitized_value = sanitize_filename_component("../Senior Developer (Lead)")

    assert "/" not in sanitized_value
    assert ".." not in sanitized_value
    assert sanitized_value
