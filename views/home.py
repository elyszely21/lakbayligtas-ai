"""Home dashboard (wireframe Screen 1)."""

import streamlit as st

from core.state import init_state

init_state()
ss = st.session_state

ADVENTURES = {
    "Hiking": ("🥾", "Day hikes and trail walks for all levels."),
    "Camping": ("⛺", "Overnight stays with the right gear and low-impact habits."),
    "Trekking": ("🏔️", "Multi-hour or multi-day routes that need more preparation."),
    "Sightseeing": ("🌄", "Scenic spots and nature visits with light activity."),
}

st.markdown("## Welcome, adventurer!")
st.write(
    "Prepare for your next outdoor trip with practical planning, gear, readiness, "
    "and safety guidance."
)
st.markdown("### Choose your adventure")
cols = st.columns(4)
for col, (name, (icon, desc)) in zip(cols, ADVENTURES.items()):
    selected = ss.adventure == name
    with col.container(
        border=True,
        key="adventure-selected" if selected else f"adventure-card-{name.lower()}",
    ):
        st.markdown(f"## {icon}")
        st.markdown(f"**{name}**")
        st.caption(desc)
        if selected:
            st.caption("Selected")
        if st.button("Select", key=f"select_{name}", use_container_width=True):
            ss.adventure = name
            ss.planner_adventure_type = name
            st.rerun()

if st.button("START PLANNING", type="primary", use_container_width=True):
    st.switch_page("views/adventure_planner.py")

st.markdown("### Quick access")
QUICK = {
    "Readiness Check": "views/readiness_assessment.py",
    "Gear Checklist": "views/gear_checklist.py",
    "Safety Guide": "views/safety_guide.py",
}
qcols = st.columns(3)
for col, (label, page) in zip(qcols, QUICK.items()):
    with col.container(border=True, key=f"quick-card-{label.lower().replace(' ', '-')}"):
        st.markdown(f"**{label}**")
        st.caption("Open practical guidance for your trip.")
        if st.button("Open", key=f"quick_{label}", use_container_width=True):
            st.switch_page(page)