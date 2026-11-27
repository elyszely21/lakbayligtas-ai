"""Shared, responsive styling for the Streamlit interface."""

import streamlit as st


def apply_styles():
    """Apply the app's small set of custom styles in one place."""
    st.markdown(
        """
        <style>
        :root {
            --ll-surface: #f3f4f4;
            --ll-card: #ffffff;
            --ll-border: #d7dcda;
            --ll-text: #242927;
            --ll-muted: #68716d;
            --ll-primary: #292f2c;
            --ll-accent: #78977f;
        }
        [data-testid="stAppViewContainer"] {
            background: var(--ll-surface);
            color: var(--ll-text);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] {
            background: #f8f9f8;
            border-right: 1px solid var(--ll-border);
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: var(--ll-text);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--ll-border);
            border-radius: 12px;
            background: var(--ll-card);
        }
        .st-key-brand-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 3rem;
            border: 1px solid var(--ll-border);
            border-radius: 10px;
            background: var(--ll-card);
            font-size: 1.35rem;
        }
        .st-key-brand-logo p { margin: 0; }
        .st-key-chat-avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 2.7rem;
            height: 2.7rem;
            border-radius: 50%;
            background: var(--ll-accent);
            color: #ffffff;
            font-weight: 700;
        }
        .st-key-chat-avatar p { margin: 0; }
        .st-key-adventure-selected [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--ll-accent);
            background: #f5f8f5;
            box-shadow: 0 0 0 1px var(--ll-accent);
        }
        [class*="st-key-adventure-card-"] [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 12rem;
        }
        button[kind="primary"] {
            background: var(--ll-primary);
            border-color: var(--ll-primary);
            color: #ffffff;
        }
        button[kind="primary"]:hover {
            background: #414944;
            border-color: #414944;
            color: #ffffff;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: #ecefed;
            border: 1px solid #e1e5e2;
            border-radius: 16px;
            padding: 0.8rem 1rem;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #ffffff;
            border: 1px solid var(--ll-border);
            border-radius: 16px;
            padding: 0.8rem 1rem;
        }
        [data-testid="stChatInput"] {
            border: 1px solid var(--ll-border);
            border-radius: 999px;
            background: #ffffff;
        }
        [data-testid="stChatInput"] button {
            border-radius: 50%;
            background: var(--ll-primary);
            color: #ffffff;
        }
        [data-testid="stChatInput"] button:hover {
            background: #414944;
            color: #ffffff;
        }
        .st-key-planner_adventure_type [role="radiogroup"] {
            gap: 0.45rem;
        }
        .st-key-planner_adventure_type [role="radiogroup"] label {
            border: 1px solid var(--ll-border);
            border-radius: 999px;
            background: #ffffff;
            padding: 0.35rem 0.8rem;
        }
        .st-key-planner_adventure_type [role="radiogroup"] label:has(input:checked) {
            border-color: var(--ll-accent);
            background: #edf3ee;
        }
        [class*="st-key-starter_"] button {
            min-height: 2.5rem;
            border: 1px solid var(--ll-border);
            border-radius: 999px;
            background: #ffffff;
            color: var(--ll-text);
        }
        [class*="st-key-starter_"] button:hover {
            border-color: var(--ll-accent);
            color: var(--ll-text);
        }
        .st-key-planner-form, .st-key-planner-result {
            min-width: 0;
        }
        @media (max-width: 700px) {
            [data-testid="stAppViewBlockContainer"] {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .stHorizontalBlock:has(.st-key-adventure-card-hiking),
            .stHorizontalBlock:has(.st-key-adventure-selected),
            .stHorizontalBlock:has(.st-key-quick-card-readiness-check) {
                flex-wrap: wrap !important;
                gap: 0.5rem;
            }
            .stHorizontalBlock:has(.st-key-adventure-card-hiking) > [data-testid="stColumn"],
            .stHorizontalBlock:has(.st-key-adventure-selected) > [data-testid="stColumn"],
            .stHorizontalBlock:has(.st-key-quick-card-readiness-check) > [data-testid="stColumn"] {
                flex: 1 1 45% !important;
                min-width: 145px;
            }
            .stHorizontalBlock:has([class*="st-key-starter_"]) {
                flex-wrap: wrap !important;
                gap: 0.4rem;
            }
            .stHorizontalBlock:has([class*="st-key-starter_"]) > [data-testid="stColumn"] {
                flex: 1 1 45% !important;
                min-width: 145px;
            }
            .stHorizontalBlock:has(.st-key-planner-form) {
                flex-direction: column !important;
            }
            .stHorizontalBlock:has(.st-key-planner-form) > [data-testid="stColumn"] {
                width: 100% !important;
                flex: 1 1 100% !important;
            }
            [class*="st-key-adventure-card-"] [data-testid="stVerticalBlockBorderWrapper"] {
                min-height: auto;
            }
            [data-testid="stChatMessage"] {
                padding: 0.65rem 0.75rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
