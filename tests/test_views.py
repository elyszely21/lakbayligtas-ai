"""Headless rendering tests for the shared layout and newly registered pages."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def render_view(filename):
    return AppTest.from_file(str(ROOT / "views" / filename), default_timeout=20).run()


def test_shared_styles_render_css():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not at.exception
    assert any("--ll-surface" in item.value for item in at.markdown)
    assert "Experience level" in {item.label for item in at.selectbox}
    assert any("local tourism office / site management" in item.value for item in at.info)


def test_home_dashboard_has_all_adventures_and_quick_links():
    at = render_view("home.py")
    assert not at.exception
    rendered = " ".join(item.value for item in at.markdown)
    assert "Welcome, adventurer!" in rendered
    assert all(name in rendered for name in ("Hiking", "Camping", "Trekking", "Sightseeing"))
    assert "START PLANNING" in {button.label for button in at.button}
    assert all(
        label in {button.label for button in at.button}
        for label in ("Open", "Select")
    )


def test_planner_layout_has_form_and_empty_result_sections():
    at = render_view("adventure_planner.py")
    assert not at.exception
    labels = {item.label for item in at.text_input}
    assert "Destination" in labels
    assert "Type of adventure" in {item.label for item in at.radio}
    assert "Additional preferences" in {item.label for item in at.text_area}
    assert "Number of days" in {item.label for item in at.number_input}
    assert "Estimated budget (PHP)" in {item.label for item in at.number_input}
    assert "GENERATE MY PLAN" in {button.label for button in at.button}
    assert "Reset" in {button.label for button in at.button}
    rendered = " ".join(item.value for item in at.markdown)
    assert all(
        heading in rendered
        for heading in ("Itinerary", "Budget estimate", "Checklist", "Before You Go")
    )


def test_placeholder_pages_render_friendly_messages():
    for filename, title in (
        ("gear_checklist.py", "Gear Checklist"),
        ("readiness_assessment.py", "Readiness Assessment"),
        ("safety_guide.py", "Safety Guide"),
    ):
        at = render_view(filename)
        assert not at.exception
        assert at.title[0].value == title
        assert "coming in the next step" in " ".join(item.value for item in at.info)


def test_home_selection_is_shared_with_planner():
    at = render_view("home.py")
    next(button for button in at.button if button.key == "select_Camping").click().run()
    assert at.session_state["adventure"] == "Camping"
    assert at.session_state["planner_adventure_type"] == "Camping"


def test_planner_preselects_home_adventure():
    at = render_view("adventure_planner.py")
    at.session_state["adventure"] = "Sightseeing"
    at.run()
    assert at.radio[0].value == "Sightseeing"
