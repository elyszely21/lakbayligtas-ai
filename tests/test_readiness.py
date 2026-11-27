import pytest

from features.readiness import assess_readiness


def test_beginner_with_long_challenging_trip_scores_not_ready_yet():
    result = assess_readiness(
        experience="Beginner",
        fitness="Moderate",
        equipment="Some gear",
        trip_days=7,
        difficulty="Challenging",
    )

    assert result["level"] == "Not ready yet"
    assert result["score"] == 4
    assert len(result["top_gaps"]) == 3
    assert {gap["area"] for gap in result["top_gaps"]} == {
        "Experience",
        "Trip duration",
        "Route difficulty",
    }
    assert all(gap["improvement_step"] for gap in result["top_gaps"])


def test_experienced_with_short_easy_trip_scores_ready():
    result = assess_readiness(
        experience="Experienced",
        fitness="Good",
        equipment="All key gear",
        trip_days=1,
        difficulty="Easy",
    )

    assert result["level"] == "Ready"
    assert result["score"] == result["maximum_score"] == 15
    assert result["top_gaps"] == []


@pytest.mark.parametrize(
    ("answers", "message"),
    [
        (
            {
                "experience": "Expert",
                "fitness": "Good",
                "equipment": "All key gear",
                "trip_days": 1,
                "difficulty": "Easy",
            },
            "Unknown experience level",
        ),
        (
            {
                "experience": "Beginner",
                "fitness": "Good",
                "equipment": "All key gear",
                "trip_days": 15,
                "difficulty": "Easy",
            },
            "Trip duration must be from 1 to 14 days",
        ),
    ],
)
def test_assessment_rejects_invalid_answers(answers, message):
    with pytest.raises(ValueError, match=message):
        assess_readiness(**answers)
