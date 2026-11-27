"""LakbayLigtas AI - entry point.

Run with:  streamlit run app.py
Sets up the page, sidebar (navigation, experience level, safety note),
the safety banner, and then runs the page the user selected.
"""

import streamlit as st

from core import prompts, styles, ui
from core.state import init_state


def sync_planner_experience():
    st.session_state["planner_experience"] = st.session_state["experience"]


st.set_page_config(page_title="LakbayLigtas AI", page_icon="🥾", layout="wide")
init_state()
styles.apply_styles()

pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/adventure_planner.py", title="Adventure Planner", icon="🧭"),
    st.Page("views/gear_checklist.py", title="Gear Checklist", icon="🎒"),
    st.Page("views/readiness_assessment.py", title="Readiness Assessment", icon="✅"),
    st.Page("views/safety_guide.py", title="Safety Guide", icon="🛟"),
    st.Page("views/chat.py", title="Chat Assistant", icon="💬"),
]
page = st.navigation(pages)

with st.sidebar:
    st.selectbox(
        "Experience level",
        prompts.EXPERIENCE_LEVELS,
        key="experience",
        on_change=sync_planner_experience,
    )
    ui.sidebar_safety_note()

ui.header()
page.run()
ui.disclaimer()
