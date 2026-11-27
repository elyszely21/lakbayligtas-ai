"""Small shared UI pieces (header and safety banner) used on every page."""

import streamlit as st


def header():
    st.markdown("## 🥾 LakbayLigtas AI")
    st.caption("Explore More. Prepare Better. Travel Responsibly.")


def disclaimer():
    st.info(
        "⚠️ LakbayLigtas AI gives general preparation advice only. It has no live weather "
        "or trail data, and all prices are estimates. Always confirm permits, fees, guide "
        "requirements, closures, and advisories with the local tourism office or site "
        "management, and check PAGASA for weather.",
        icon=None,
    )


def sidebar_safety_note():
    st.caption(
        "🛟 In an emergency, contact local emergency services or local authorities "
        "right away. This app cannot call for help."
    )
