"""Interactive, offline gear checklist for common outdoor activities."""

import streamlit as st

from core.state import init_state
from features.checklist import GEAR_CATALOG, export_markdown

init_state()
ss = st.session_state

st.title("Gear Checklist")

activities = tuple(GEAR_CATALOG)
if "checklist_activity" not in ss:
    selected = ss.get("adventure")
    ss.checklist_activity = selected if selected in activities else activities[0]

activity = st.selectbox("Activity", activities, key="checklist_activity")
groups = GEAR_CATALOG[activity]

essential_items = [
    item
    for items in groups.values()
    for item in items
    if item["priority"] == "essential"
]
optional_items = [
    item
    for items in groups.values()
    for item in items
    if item["priority"] == "optional"
]
all_items = essential_items + optional_items
checked_ids = []
for item in all_items:
    checkbox_key = f"checklist_{activity.lower()}_{item['id']}"
    if ss.get(checkbox_key, False):
        checked_ids.append(item["id"])

completed = len(checked_ids)
progress = completed / len(all_items) if all_items else 0
st.progress(progress, text=f"Completed {completed} of {len(all_items)} items")

for priority, items in (("Essential", essential_items), ("Optional", optional_items)):
    st.subheader(f"{priority} items")
    if not items:
        st.caption(f"No {priority.lower()} items for this activity.")
        continue

    for group, group_items in groups.items():
        matching_items = [item for item in group_items if item["priority"] == priority.lower()]
        if not matching_items:
            continue
        st.markdown(f"**{group}**")
        for item in matching_items:
            checkbox_key = f"checklist_{activity.lower()}_{item['id']}"
            st.checkbox(item["name"], key=checkbox_key)

    if priority == "Essential":
        st.divider()

st.download_button(
    "Download checklist (Markdown)",
    data=export_markdown(activity, checked_ids),
    file_name=f"{activity.lower()}-gear-checklist.md",
    mime="text/markdown",
    use_container_width=True,
)
