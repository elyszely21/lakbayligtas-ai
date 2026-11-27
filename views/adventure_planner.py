"""Adventure Planner layout; plan generation is implemented in a later task."""

import streamlit as st

from core import prompts
from core.state import init_state

init_state()
ss = st.session_state


def reset_planner():
    for key in (
        "planner_destination",
        "planner_days",
        "planner_budget",
        "planner_preferences",
        "planner_adventure_type",
    ):
        ss.pop(key, None)
    ss.adventure = None


def sync_adventure_type():
    ss.adventure = ss.planner_adventure_type


st.title("Adventure Planner")
form_col, result_col = st.columns([1, 1], gap="large")

with form_col.container(border=True, key="planner-form"):
    st.subheader("Trip details")
    st.text_input("Destination", key="planner_destination")
    adventure_types = ("Hiking", "Camping", "Trekking", "Sightseeing")
    selected_type = ss.adventure if ss.adventure in adventure_types else "Hiking"
    selected_index = adventure_types.index(selected_type)
    ss.planner_adventure_type = selected_type
    selected_adventure = st.radio(
        "Type of adventure",
        adventure_types,
        index=selected_index,
        horizontal=True,
        key="planner_adventure_type",
        on_change=sync_adventure_type,
        label_visibility="collapsed",
    )
    ss.adventure = selected_adventure
    ss.setdefault("planner_experience", ss.experience)
    st.selectbox(
        "Experience level",
        prompts.EXPERIENCE_LEVELS,
        key="planner_experience",
        on_change=lambda: setattr(ss, "experience", ss.planner_experience),
    )
    days_col, budget_col = st.columns(2)
    with days_col:
        st.number_input("Number of days", min_value=1, value=2, step=1, key="planner_days")
    with budget_col:
        st.number_input(
            "Estimated budget (PHP)",
            min_value=0,
            value=0,
            step=500,
            key="planner_budget",
        )
    st.text_area("Additional preferences", key="planner_preferences")
    generate_col, reset_col = st.columns([2, 1])
    with generate_col:
        if st.button("GENERATE MY PLAN", type="primary", use_container_width=True):
            st.info("Plan generation is coming in the next step.")
    with reset_col:
        st.button("Reset", on_click=reset_planner, use_container_width=True)

with result_col.container(border=True, key="planner-result"):
    st.subheader("Your plan (result area)")
    for section in ("Itinerary", "Budget estimate", "Checklist", "Before You Go"):
        st.markdown(f"**{section}**")
        st.caption("Your plan details will appear here.")
