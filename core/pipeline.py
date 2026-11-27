"""Shared safety pipeline for user text sent to the language model."""

from dataclasses import dataclass

from core import llm_client, prompts, security


@dataclass
class PipelineResult:
    ok: bool
    text: str = ""
    error: str = ""
    blocked_reason: str = ""
    output_blocked: bool = False
    called: bool = False
    estimated_ak: float = 0.0


def _send(history, token, experience_level, max_tokens=None):
    messages = prompts.build_messages(history, token, experience_level)
    result = llm_client.ask(messages, max_tokens=max_tokens)
    if not result.ok:
        return PipelineResult(
            ok=False,
            error=result.error,
            called=True,
            estimated_ak=result.estimated_ak,
        )

    if not security.check_output(result.text, prompts.SYSTEM_PROMPT):
        return PipelineResult(
            ok=True,
            text=security.OUTPUT_BLOCK_MESSAGE,
            output_blocked=True,
            called=True,
            estimated_ak=result.estimated_ak,
        )

    return PipelineResult(
        ok=True,
        text=result.text,
        called=True,
        estimated_ak=result.estimated_ak,
    )


def ask_history(history, token, experience_level="Beginner", max_tokens=None):
    """Validate all user turns, wrap them, call the LLM once, and check its reply."""
    cleaned_history = []
    for message in history:
        cleaned_message = dict(message)
        if message["role"] == "user":
            checked = security.check_input(message["content"])
            if not checked.ok:
                return PipelineResult(
                    ok=False,
                    error=security.REFUSAL_MESSAGE,
                    blocked_reason=checked.reason,
                )
            cleaned_message["content"] = checked.cleaned
        cleaned_history.append(cleaned_message)
    return _send(
        llm_client.trim_history(cleaned_history),
        token,
        experience_level,
        max_tokens,
    )


def ask_fields(fields, instruction, token, experience_level="Beginner", max_tokens=None):
    """Validate each free-text field before combining, wrapping, and sending once."""
    history = [{"role": "user", "content": instruction}]
    for label, value in fields.items():
        if value is None or value == "":
            continue
        checked = security.check_input(str(value))
        if not checked.ok:
            return PipelineResult(
                ok=False,
                error=security.REFUSAL_MESSAGE,
                blocked_reason=checked.reason,
            )
        history.append({"role": "user", "content": f"{label}: {checked.cleaned}"})
    return _send(history, token, experience_level, max_tokens)
