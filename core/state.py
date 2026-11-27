"""Session-state helpers for LakbayLigtas AI.

Streamlit re-runs the script on every click, so anything that must survive
(chat history, random token, counters) is kept in st.session_state.
"""

import streamlit as st

from core import security


def init_state():
    ss = st.session_state
    ss.setdefault("token", security.new_session_token())
    # each message: {"role", "content", "blocked": bool, "note": str}
    ss.setdefault("messages", [])
    ss.setdefault("user_msg_count", 0)
    ss.setdefault("total_ak", 0.0)
    ss.setdefault("experience", "Beginner")
    ss.setdefault("pending_prompt", None)
    ss.setdefault("adventure", None)
