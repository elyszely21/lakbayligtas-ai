import pytest

from features.planner import split_plan_sections, validate_form


@pytest.mark.parametrize(
    ("destination", "days", "budget", "people", "expected_error"),
    [
        ("", 2, 0, 1, "Enter a destination."),
        ("Cebu", 0, 0, 1, "Number of days must be from 1 to 7."),
        ("Cebu", 8, 0, 1, "Number of days must be from 1 to 7."),
        ("Cebu", 2, -1, 1, "Estimated budget must be zero or more."),
        ("Cebu", 2, float("nan"), 1, "Estimated budget must be zero or more."),
        ("Cebu", 2, 0, 0, "Number of people must be at least 1."),
    ],
)
def test_form_validation_reports_invalid_values(
    destination, days, budget, people, expected_error
):
    assert expected_error in validate_form(destination, days, budget, people)


def test_form_validation_accepts_valid_values():
    assert validate_form("Cebu", 7, 0, 3) == []


def test_split_plan_sections_requires_both_sections():
    assert split_plan_sections("## Itinerary\nWalk to the campsite.") is None


def test_split_plan_sections_extracts_itinerary_and_before_you_go():
    reply = (
        "## Itinerary\nStart early and take regular breaks.\n"
        "## Before You Go\nVerify permits with local authorities and check PAGASA."
    )
    assert split_plan_sections(reply) == {
        "itinerary": "Start early and take regular breaks.",
        "before_you_go": "Verify permits with local authorities and check PAGASA.",
    }
