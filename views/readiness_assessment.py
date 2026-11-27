"""Short, deterministic outdoor trip readiness self-check."""

import streamlit as st

from core.prompts import EXPERIENCE_LEVELS
from core.state import init_state
from features.readiness import assess_readiness

init_state()
ss = st.session_state

st.title("Readiness Assessment")
st.write(
    "Answer a few questions about your experience, preparation, and planned trip."
)

default_experience = ss.experience if ss.experience in EXPERIENCE_LEVELS else "Beginner"
with st.form("readiness-assessment"):
    experience = st.selectbox(
        "Experience level",
        EXPERIENCE_LEVELS,
        index=EXPERIENCE_LEVELS.index(default_experience),
        key="readiness_experience",
    )
    fitness = st.selectbox(
        "How would you rate your current fitness?",
        ("Low", "Moderate", "Good"),
        key="readiness_fitness",
    )
    equipment = st.selectbox(
        "How prepared is your equipment?",
        ("No gear yet", "Some gear", "All key gear"),
        key="readiness_equipment",
    )
    trip_days = st.number_input(
        "How many days is your trip?",
        min_value=1,
        max_value=14,
        value=2,
        step=1,
        key="readiness_days",
    )
    difficulty = st.selectbox(
        "How would you describe the route difficulty?",
        ("Easy", "Moderate", "Challenging"),
        key="readiness_difficulty",
    )
    submitted = st.form_submit_button("Check my readiness", type="primary")

if submitted:
    ss.readiness_result = assess_readiness(
        experience=experience,
        fitness=fitness,
        equipment=equipment,
        trip_days=trip_days,
        difficulty=difficulty,
    )

if ss.get("readiness_result"):
    result = ss.readiness_result
    st.subheader("Your self-check result")
    st.markdown(f"### {result['level']}")
    st.caption(f"Self-check score: {result['score']} of {result['maximum_score']}")

    st.markdown("#### Top areas to work on")
    if result["top_gaps"]:
        for gap in result["top_gaps"]:
            st.markdown(f"**{gap['area']}** — {gap['reason']}")
            st.write(f"Improvement step: {gap['improvement_step']}")
    else:
        st.write(
            "No specific gaps were flagged by these answers. Keep preparing and "
            "confirm trip details with local authorities."
        )

st.info("This is a self-check only.")
