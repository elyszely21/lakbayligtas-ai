"""Chat assistant (wireframe Screen 2).

Every typed message goes through the defense pipeline:
input filter -> random token + XML wrap -> system prompt + sandwich reminder
-> LLM -> output check.
"""

import streamlit as st

from core import config, llm_client, prompts, security
from core.state import init_state

init_state()
ss = st.session_state

MAX_MESSAGES = config.get_int("MAX_USER_MESSAGES", 15)

WELCOME = (
    "Hi, I'm **LakbayLigtas AI**, your outdoor preparation assistant. 🥾\n\n"
    "Tell me where you want to go, what activity you have in mind, and how much "
    "experience you have, and I'll help with a plan, a packing checklist, a budget "
    "estimate, or a readiness check."
)

STARTERS = [
    "Plan my first hike",
    "What should I pack?",
    "Am I ready for a trek?",
    "Budget-friendly trip",
]


def queue_prompt(text):
    ss.pending_prompt = text


def clear_chat():
    ss.messages = []
    ss.token = security.new_session_token()


def show_message(msg):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("note"):
            st.caption(msg["note"])


def handle(prompt):
    check = security.check_input(prompt)
    if check.reason == "empty":
        return

    with st.chat_message("user"):
        st.markdown(prompt)

    # Defense 1: input filtering. Blocked messages never reach the LLM.
    if not check.ok:
        if check.reason == "too_long":
            reply = f"Your message is too long. Please keep it under {security.MAX_INPUT_CHARS} characters."
            note = "🛡️ Blocked by input validation (message too long)."
        else:
            reply = security.REFUSAL_MESSAGE
            note = "🛡️ Blocked by the input filter (possible prompt-injection attempt). Nothing was sent to the AI."
        user_msg = {"role": "user", "content": prompt, "blocked": True, "note": ""}
        bot_msg = {"role": "assistant", "content": reply, "blocked": True, "note": note}
        ss.messages += [user_msg, bot_msg]
        show_message(bot_msg)
        return

    if ss.user_msg_count >= MAX_MESSAGES:
        st.warning(
            f"You have reached the limit of {MAX_MESSAGES} messages for this session. "
            "Refresh the page to start a new session."
        )
        return

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in ss.messages
        if not m.get("blocked")
    ]
    history.append({"role": "user", "content": check.cleaned})
    llm_messages = prompts.build_messages(
        llm_client.trim_history(history), ss.token, ss.experience
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = llm_client.ask(llm_messages)
        if not result.ok:
            st.error(result.error + " Your message was not sent, so please try again.")
            return

        reply, note = result.text, ""
        # Defense 5: output check for leaked system-prompt text.
        if not security.check_output(reply, prompts.SYSTEM_PROMPT):
            reply = security.OUTPUT_BLOCK_MESSAGE
            note = "🛡️ The reply was replaced by the output check."
        st.markdown(reply)
        if note:
            st.caption(note)

    ss.messages.append({"role": "user", "content": check.cleaned, "blocked": False, "note": ""})
    ss.messages.append({"role": "assistant", "content": reply, "blocked": False, "note": note})
    ss.user_msg_count += 1
    ss.total_ak += result.estimated_ak


top_left, top_right = st.columns([4, 1])
top_left.markdown("### 💬 Chat Assistant")
top_right.button("Clear chat", on_click=clear_chat, use_container_width=True)

for message in ss.messages:
    show_message(message)

if not ss.messages:
    with st.chat_message("assistant"):
        st.markdown(WELCOME)
    st.caption("Suggested conversation starters")
    cols = st.columns(len(STARTERS))
    for col, text in zip(cols, STARTERS):
        col.button(text, key=f"starter_{text}", on_click=queue_prompt, args=(text,), use_container_width=True)

typed = st.chat_input("Type your message here...", max_chars=security.MAX_INPUT_CHARS)
prompt = typed or ss.pop("pending_prompt", None)
if prompt:
    handle(prompt)

st.caption(
    f"Messages used: {ss.user_msg_count}/{MAX_MESSAGES} · "
    f"Estimated credits used this session: {ss.total_ak:.1f} AK"
)
