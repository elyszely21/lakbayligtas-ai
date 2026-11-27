"""Validation and response parsing helpers for the Adventure Planner."""

import math
import re


def validate_form(destination, days, budget, people=1):
    """Return a list of form errors without making any LLM calls."""
    errors = []
    if not isinstance(destination, str) or not destination.strip():
        errors.append("Enter a destination.")
    if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 7:
        errors.append("Number of days must be from 1 to 7.")
    if (
        isinstance(budget, bool)
        or not isinstance(budget, (int, float))
        or not math.isfinite(budget)
        or budget < 0
    ):
        errors.append("Estimated budget must be zero or more.")
    if isinstance(people, bool) or not isinstance(people, int) or people < 1:
        errors.append("Number of people must be at least 1.")
    return errors


def split_plan_sections(text):
    """Extract the required Itinerary and Before You Go headings from a reply."""
    heading = re.compile(r"(?im)^\s*#{1,3}\s*(Itinerary|Before You Go)\s*:?\s*$")
    matches = list(heading.finditer(text))
    sections = {}
    for index, match in enumerate(matches):
        name = match.group(1).lower()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[name] = text[match.end() : end].strip()

    itinerary = sections.get("itinerary", "")
    before_you_go = sections.get("before you go", "")
    if not itinerary or not before_you_go:
        return None
    return {"itinerary": itinerary, "before_you_go": before_you_go}
