from __future__ import annotations

from typing import Any

from infrastructure.pdf_renderer import CvPdfRenderer
from tests.helpers.style_helpers import load_project_style_configuration


class FakeBoundLogger:
    def __init__(self) -> None:
        self.bound_context: dict[str, Any] = {}
        self.warning_events: list[tuple[dict[str, Any], str]] = []
        self.info_events: list[tuple[dict[str, Any], str]] = []

    def bind(self, **kwargs: Any) -> "FakeBoundLogger":
        updated_context = dict(self.bound_context)
        updated_context.update(kwargs)
        self.bound_context = updated_context
        return self

    def warning(self, message: str) -> None:
        self.warning_events.append((dict(self.bound_context), message))

    def info(self, message: str) -> None:
        self.info_events.append((dict(self.bound_context), message))


def test_renderer_warns_for_unknown_section_type() -> None:
    renderer = CvPdfRenderer(
        language="pt",
        translations={},
        visual_settings=load_project_style_configuration(),
    )
    styles = renderer.pdf_style_engine.build_stylesheet()
    elements: list[Any] = []
    fake_logger = FakeBoundLogger()
    cv_data = {
        "sections": [
            {"type": "unknown_section", "enabled": True, "order": 1},
        ],
        "unknown_section": [{"name": "unexpected item"}],
    }

    renderer._add_dynamic_sections(elements, styles, cv_data, fake_logger)

    assert len(fake_logger.warning_events) == 1
    warning_context, warning_message = fake_logger.warning_events[0]
    assert warning_context.get("step") == "unknown_section"
    assert warning_message == "Unknown section type; skipping section"


def test_renderer_resolves_section_order_from_configuration() -> None:
    renderer = CvPdfRenderer(
        language="pt",
        translations={},
        visual_settings=load_project_style_configuration(),
    )
    cv_data = {
        "sections": [
            {"type": "skills", "enabled": True, "order": 3},
            {"type": "education", "enabled": True, "order": 2},
            {"type": "experience", "enabled": True, "order": 1},
            {"type": "education", "enabled": True, "order": 4},
            {"type": "languages", "enabled": False, "order": 5},
        ]
    }

    section_order = renderer._resolve_sections_to_render(cv_data)

    assert section_order == ["experience", "education", "skills"]
