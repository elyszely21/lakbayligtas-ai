"""Adventure Planner form, budget estimates, and one-call trip plan generation."""

import streamlit as st

from core import config, pipeline, prompts
from core.state import init_state
from features.budget import estimate_budget
from features.planner import split_plan_sections, validate_form

init_state()
ss = st.session_state


def reset_planner():
    for key in (
        "planner_destination",
        "planner_days",
        "planner_budget",
        "planner_people",
        "planner_preferences",
        "planner_adventure_type",
        "planner_result",
        "planner_error",
    ):
        ss.pop(key, None)
    ss.adventure = None


def sync_adventure_type():
    ss.adventure = ss.planner_adventure_type


def generate_plan():
    destination = ss.get("planner_destination", "")
    days = ss.get("planner_days", 2)
    budget = ss.get("planner_budget", 0)
    people = ss.get("planner_people", 1)
    preferences = ss.get("planner_preferences", "")
    errors = validate_form(destination, days, budget, people)
    ss.planner_error = ""
    ss.planner_result = None

    if errors:
        ss.planner_error = " ".join(errors)
        return
    if ss.user_msg_count >= config.get_int("MAX_USER_MESSAGES", 15):
        ss.planner_error = (
            f"You have reached the limit of {config.get_int('MAX_USER_MESSAGES', 15)} "
            "messages for this session."
        )
        return

    estimates = estimate_budget(people, days)
    adventure_type = ss.get("adventure", "Hiking") or "Hiking"
    experience = ss.get("planner_experience", ss.experience)
    instruction = (
        "Create a concise, practical outdoor-trip plan using the supplied details. "
        "Return exactly these two markdown sections: ## Itinerary and ## Before You Go. "
        "Do not calculate or invent any prices, weather, trail conditions, permits, fees, "
        "closures, or transport schedules. All prices are handled separately by the app. "
        "In Before You Go, tell the user to verify permits and advisories with the local "
        "tourism office / site management and check PAGASA for weather."
    )
    fields = {
        "Destination": destination,
        "Adventure type": adventure_type,
        "Experience level": experience,
        "Number of people": people,
        "Number of days": days,
        "User's budget in PHP": budget,
        "Additional preferences": preferences,
    }

    result = pipeline.ask_fields(
        fields,
        instruction,
        ss.token,
        experience,
        max_tokens=500,
    )
    if result.called:
        ss.user_msg_count += 1
        ss.total_ak += result.estimated_ak

    if not result.ok:
        if result.blocked_reason:
            ss.planner_error = (
                "A form field was blocked by the input filter. Please revise the text "
                "and try again; it was not sent to the AI."
            )
        else:
            ss.planner_error = result.error
        ss.planner_result = {"budget": estimates}
        return

    if result.output_blocked:
        ss.planner_error = "The AI reply was blocked by the output safety check."
        ss.planner_result = {"budget": estimates}
        return

    sections = split_plan_sections(result.text)
    if sections is None:
        ss.planner_error = (
            "The AI reply did not include both required sections. Please try again."
        )
        ss.planner_result = {"budget": estimates}
        return

    ss.planner_result = {
        "itinerary": sections["itinerary"],
        "budget": estimates,
        "before_you_go": sections["before_you_go"],
        "checklist_ready": False,
    }


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
    people_col, days_col, budget_col = st.columns(3)
    with people_col:
        st.number_input("Number of people", min_value=1, value=1, step=1, key="planner_people")
    with days_col:
        st.number_input(
            "Number of days",
            min_value=1,
            max_value=7,
            value=2,
            step=1,
            key="planner_days",
        )
    with budget_col:
        st.number_input(
            "Estimated budget (PHP)",
            min_value=0,
            value=0,
            step=500,
            key="planner_budget",
        )
    st.text_area("Additional preferences", key="planner_preferences")
    if ss.get("planner_error"):
        st.error(ss.planner_error)
    generate_col, reset_col = st.columns([2, 1])
    with generate_col:
        st.button(
            "GENERATE MY PLAN",
            type="primary",
            use_container_width=True,
            on_click=generate_plan,
        )
    with reset_col:
        st.button("Reset", on_click=reset_planner, use_container_width=True)

with result_col.container(border=True, key="planner-result"):
    st.subheader("Your plan (result area)")
    result = ss.get("planner_result")
    st.markdown("**Itinerary**")
    if result and result.get("itinerary"):
        st.markdown(result["itinerary"])
    else:
        st.caption("Your itinerary will appear here after you generate a plan.")

    st.markdown("**Budget estimate**")
    if result and result.get("budget"):
        budget_rows = [
            {
                "Category": details["label"],
                "Low": f"PHP {details['low']:,} ESTIMATE",
                "High": f"PHP {details['high']:,} ESTIMATE",
            }
            for details in result["budget"].values()
        ]
        st.table(budget_rows)
        st.caption(
            "These are ESTIMATES. Verify prices locally with the tourism office / "
            "site management."
        )
    else:
        st.caption("Your budget estimate will appear here after you generate a plan.")

    st.markdown("**Checklist**")
    if result:
        st.info("Checklist guidance will be connected from features/checklist.py in Task 3.")
    else:
        st.caption("Your checklist will appear here after you generate a plan.")

    st.markdown("**Before You Go**")
    if result and result.get("before_you_go"):
        st.markdown(result["before_you_go"])
    else:
        st.caption("Your verification reminders will appear here after you generate a plan.")
    st.caption(
        "Verify permits and advisories with the local tourism office / site management; "
        "check PAGASA for weather."
    )
