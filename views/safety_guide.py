"""General outdoor safety guidance using the shared LLM safety pipeline."""

import streamlit as st

from core import config, pipeline, security
from core.state import init_state

init_state()
ss = st.session_state

SCENARIOS = {
    "Group separated": "What general steps should I take if my outdoor group becomes separated?",
    "Sudden rain": "What general steps should I take if sudden rain starts during an outdoor trip?",
    "Injury": "What general steps should a group take if someone is injured outdoors?",
    "Lost signal": "What general steps should I take if I lose phone signal outdoors?",
    "Running out of water": "What general steps should I take if my group is running low on water?",
    "Getting lost": "What general steps should I take if I realize I am lost outdoors?",
}

INSTRUCTIONS = (
    "Give 3 to 5 concise, numbered general steps for this outdoor safety question. "
    "Do not diagnose, promise safety, or invent weather, trail conditions, local "
    "emergency numbers, closures, or other live facts. Keep the guidance calm and "
    "practical. If the situation is real or urgent, advise contacting local authorities "
    "or emergency services immediately."
)


def ask_safety_question(question):
    ss.safety_answer = ""
    ss.safety_error = ""
    if not question or not question.strip():
        ss.safety_error = "Enter a safety question first."
        return

    message_limit = config.get_int("MAX_USER_MESSAGES", 15)
    if ss.user_msg_count >= message_limit:
        ss.safety_error = f"You have reached the limit of {message_limit} messages for this session."
        return

    result = pipeline.ask_fields(
        {"Safety question": question},
        INSTRUCTIONS,
        ss.token,
        ss.experience,
        max_tokens=300,
    )
    if result.called:
        ss.user_msg_count += 1
        ss.total_ak += result.estimated_ak

    if not result.ok:
        if result.blocked_reason:
            ss.safety_error = (
                "That question was blocked by the input filter and was not sent to the AI. "
                "Please rephrase it as an outdoor safety question."
            )
        else:
            ss.safety_error = result.error
        return

    ss.safety_answer = result.text
    if result.output_blocked:
        ss.safety_error = "The reply was replaced by the output safety check."


st.title("Safety Guide")
st.write("Choose a common situation or ask a general outdoor safety question.")

st.subheader("Common situations")
scenario_columns = st.columns(3)
for index, (label, question) in enumerate(SCENARIOS.items()):
    with scenario_columns[index % len(scenario_columns)]:
        st.button(
            label,
            key=f"safety_scenario_{index}",
            use_container_width=True,
            on_click=ask_safety_question,
            args=(question,),
        )

st.subheader("Ask a question")
with st.form("safety-question-form"):
    free_text = st.text_input(
        "Your safety question",
        max_chars=security.MAX_INPUT_CHARS,
        key="safety_free_text",
    )
    submitted = st.form_submit_button("Ask", type="primary")
if submitted:
    ask_safety_question(free_text)

if ss.get("safety_error"):
    st.error(ss.safety_error)
if ss.get("safety_answer"):
    st.markdown("### General steps")
    st.markdown(ss.safety_answer)
    st.info(
        "If this is a real or urgent situation, contact local authorities or emergency "
        "services immediately."
    )

st.caption(
    "General preparation guidance only; this page has no live weather, trail, or "
    "emergency-service information."
)
