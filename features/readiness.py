"""Deterministic self-check scoring for outdoor trip readiness."""

EXPERIENCE_SCORES = {
    "Beginner": 0,
    "Intermediate": 2,
    "Experienced": 3,
}
FITNESS_SCORES = {
    "Low": 0,
    "Moderate": 2,
    "Good": 3,
}
EQUIPMENT_SCORES = {
    "No gear yet": 0,
    "Some gear": 2,
    "All key gear": 3,
}
DIFFICULTY_SCORES = {
    "Easy": 3,
    "Moderate": 2,
    "Challenging": 0,
}
MAX_SCORE = 15


def assess_readiness(experience, fitness, equipment, trip_days, difficulty):
    """Score answers and return a level plus up to three improvement areas."""
    if experience not in EXPERIENCE_SCORES:
        raise ValueError(f"Unknown experience level: {experience}")
    if fitness not in FITNESS_SCORES:
        raise ValueError(f"Unknown fitness level: {fitness}")
    if equipment not in EQUIPMENT_SCORES:
        raise ValueError(f"Unknown equipment level: {equipment}")
    if difficulty not in DIFFICULTY_SCORES:
        raise ValueError(f"Unknown difficulty: {difficulty}")
    if (
        isinstance(trip_days, bool)
        or not isinstance(trip_days, int)
        or not 1 <= trip_days <= 14
    ):
        raise ValueError("Trip duration must be from 1 to 14 days")

    duration_score = 3 if trip_days <= 2 else 2 if trip_days <= 4 else 1 if trip_days <= 6 else 0
    dimensions = [
        (
            "Experience",
            EXPERIENCE_SCORES[experience],
            f"You selected {experience.lower()} experience.",
            "Build experience through shorter, guided outings before attempting longer or harder routes.",
        ),
        (
            "Fitness preparation",
            FITNESS_SCORES[fitness],
            f"You rated your current fitness as {fitness.lower()}.",
            "Build gradually with manageable walks and breaks that suit your current ability.",
        ),
        (
            "Equipment",
            EQUIPMENT_SCORES[equipment],
            {
                "No gear yet": "You have not gathered the key trip equipment yet.",
                "Some gear": "Some trip equipment may still be missing.",
                "All key gear": "",
            }[equipment],
            "Make a checklist of essential gear and learn how to use it before departure.",
        ),
        (
            "Trip duration",
            duration_score,
            f"The trip is {trip_days} days long.",
            "Consider a shorter itinerary or breaking a long trip into manageable stages.",
        ),
        (
            "Route difficulty",
            DIFFICULTY_SCORES[difficulty],
            f"You selected {difficulty.lower()} route difficulty.",
            "Consider easier terrain and ask qualified local guides or site management for current route guidance.",
        ),
    ]

    score = sum(dimension[1] for dimension in dimensions)
    if score <= 5:
        level = "Not ready yet"
    elif score <= 10:
        level = "Almost ready"
    else:
        level = "Ready"

    gaps = [
        {
            "area": name,
            "reason": reason,
            "improvement_step": step,
            "gap_score": 3 - points,
        }
        for name, points, reason, step in dimensions
        if points < 3 and reason
    ]
    gaps.sort(key=lambda gap: gap["gap_score"], reverse=True)

    return {
        "score": score,
        "maximum_score": MAX_SCORE,
        "level": level,
        "top_gaps": gaps[:3],
    }
