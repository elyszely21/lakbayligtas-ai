import pytest

from features.budget import estimate_budget


def test_budget_estimates_scale_trip_and_daily_costs():
    estimates = estimate_budget(people=2, days=3)

    assert estimates["transport"]["low"] == 400
    assert estimates["transport"]["high"] == 3000
    assert estimates["food_water"]["low"] == 1800
    assert estimates["food_water"]["high"] == 4800
    assert estimates["fees_guide"]["low"] == 200
    assert estimates["fees_guide"]["high"] == 3000
    assert estimates["gear_rental"]["low"] == 0
    assert estimates["gear_rental"]["high"] == 4200
    assert estimates["total"]["low"] == 2400
    assert estimates["total"]["high"] == 15000


@pytest.mark.parametrize(
    ("people", "days"),
    [(0, 1), (-1, 1), (1, 0), (1, -2), (True, 1), (1, True), (1.5, 1)],
)
def test_budget_rejects_invalid_counts(people, days):
    with pytest.raises(ValueError):
        estimate_budget(people, days)
