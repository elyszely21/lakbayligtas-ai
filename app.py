"""LakbayLigtas AI - entry point.

Run with:  streamlit run app.py
Sets up the page, sidebar (navigation, experience level, safety note),
the safety banner, and then runs the page the user selected.
"""

import streamlit as st

from core import prompts, ui
from core.state import init_state

st.set_page_config(page_title="LakbayLigtas AI", page_icon="🥾", layout="wide")
init_state()

pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/chat.py", title="Chat Assistant", icon="💬"),
]
page = st.navigation(pages)

with st.sidebar:
    st.selectbox("Experience level", prompts.EXPERIENCE_LEVELS, key="experience")
    ui.sidebar_safety_note()

ui.header()
ui.disclaimer()
page.run()
