"""Small shared UI pieces (header and safety banner) used on every page."""

import streamlit as st


def header():
    logo_col, title_col, help_col = st.columns([0.7, 7, 1.2], vertical_alignment="center")
    with logo_col.container(key="brand-logo"):
        st.markdown("🥾")
    with title_col:
        st.markdown("**LakbayLigtas AI**")
        st.caption("Explore More. Prepare Better. Travel Responsibly.")
    with help_col:
        with st.popover("Help", use_container_width=True):
            st.markdown("### How to use LakbayLigtas AI")
            st.write(
                "Choose a page from the sidebar, enter your trip details, and use "
                "Chat Assistant for outdoor-preparation questions. Verify current "
                "conditions and requirements with official local sources."
            )


def disclaimer():
    st.info(
        "LakbayLigtas AI provides general preparation advice only; it has no live "
        "weather or trail data. All prices are ESTIMATES. Verify permits and advisories "
        "with the local tourism office / site management, and check PAGASA for weather.",
        icon=None,
    )


def sidebar_safety_note():
    st.caption(
        "In an emergency, contact local emergency services or local authorities. "
        "This app cannot call for help."
    )
