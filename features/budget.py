"""Pure-Python trip budget estimates loaded from the project data file."""

import json
from pathlib import Path


_COST_FILE = Path(__file__).resolve().parent.parent / "data" / "cost_estimates.json"


def estimate_budget(people, days):
    """Return low/high PHP estimates for each cost category and the trip total."""
    if isinstance(people, bool) or not isinstance(people, int) or people < 1:
        raise ValueError("people must be a positive whole number")
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise ValueError("days must be a positive whole number")

    with _COST_FILE.open(encoding="utf-8") as cost_file:
        cost_data = json.load(cost_file)

    estimates = {}
    total_low = 0
    total_high = 0
    if cost_data.get("currency") != "PHP" or cost_data.get("values_are") != "ESTIMATES":
        raise ValueError("Cost estimates must be labeled in PHP as ESTIMATES")

    for category, details in cost_data["categories"].items():
        multiplier = people * (days if details["unit"] == "per_person_day" else 1)
        low = details["low"] * multiplier
        high = details["high"] * multiplier
        estimates[category] = {
            "label": details["label"],
            "unit": details["unit"],
            "low": low,
            "high": high,
        }
        total_low += low
        total_high += high

    estimates["total"] = {
        "label": "Total",
        "unit": "trip",
        "low": total_low,
        "high": total_high,
    }
    return estimates
