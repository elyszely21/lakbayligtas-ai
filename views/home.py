"""Home dashboard (wireframe Screen 1)."""

import streamlit as st

from core.state import init_state

init_state()
ss = st.session_state

st.subheader("Welcome, adventurer!")
st.write(
    "Tell me about your trip and I'll help you prepare: a plan, a packing checklist, "
    "a budget estimate, and a readiness check. Pick an adventure type to begin."
)

ADVENTURES = {
    "Hiking": ("🥾", "Day hikes and trail walks for all levels."),
    "Camping": ("⛺", "Overnight stays with the right gear and low-impact habits."),
    "Trekking": ("🏔️", "Multi-hour or multi-day routes that need more preparation."),
    "Sightseeing": ("🌄", "Scenic spots and nature visits with light activity."),
}

st.markdown("#### Choose your adventure")
cols = st.columns(4)
for col, (name, (icon, desc)) in zip(cols, ADVENTURES.items()):
    with col.container(border=True):
        st.markdown(f"### {icon} {name}")
        st.caption(desc)
        if ss.adventure == name:
            st.success("Selected")
        elif st.button("Select", key=f"select_{name}"):
            ss.adventure = name
            st.rerun()

if st.button("START PLANNING", type="primary"):
    kind = (ss.adventure or "outdoor").lower()
    ss.pending_prompt = f"I want to plan a trip. Activity: {kind}. Please ask me what you need to know."
    st.switch_page("views/chat.py")

st.markdown("#### Quick access")
QUICK = {
    "Readiness Check": "Am I ready for a trek? Please check my readiness.",
    "Gear Checklist": "What should I pack? Please give me a gear checklist.",
    "Safety Guide": "What if our group gets separated on the trail?",
}
qcols = st.columns(3)
for col, (label, prompt) in zip(qcols, QUICK.items()):
    with col.container(border=True):
        st.markdown(f"**{label}**")
        if st.button("Open in chat", key=f"quick_{label}"):
            ss.pending_prompt = prompt
            st.switch_page("views/chat.py")