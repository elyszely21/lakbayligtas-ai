"""LLM client for LakbayLigtas AI (Aiki Labs, OpenAI-compatible API).

One function, ask(), sends messages to the model and returns an LLMResult.
Features never call the API directly. Errors become friendly messages and
the API key is never included in any message shown to the user.
There are no automatic retries, because every call spends shared credits.
"""

from dataclasses import dataclass

import requests

from core import config


@dataclass
class LLMResult:
    ok: bool
    text: str = ""
    error: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def estimated_ak(self):
        """Rough Aikredits used: 1 AK is about 100 input or 20 output tokens."""
        return round(self.prompt_tokens / 100 + self.completion_tokens / 20, 1)


def trim_history(history, max_messages=None):
    """Keep only the most recent messages so each call stays cheap."""
    if max_messages is None:
        max_messages = config.get_int("MAX_HISTORY_MESSAGES", 8)
    trimmed = history[-max_messages:]
    # The first message sent should be from the user.
    while trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]
    return trimmed


def ask(messages, max_tokens=None):
    api_key = config.get_api_key()
    if not api_key:
        return LLMResult(
            ok=False,
            error="The AI service is not configured yet. Add LLM_API_KEY to the app secrets.",
        )

    base_url = str(config.get_setting("LLM_BASE_URL")).rstrip("/")
    limit = max_tokens or config.get_int("LLM_MAX_OUTPUT_TOKENS", 600)
    limit = min(limit, 800)  # the course key allows at most 800

    payload = {
        "model": config.get_setting("LLM_MODEL"),
        "messages": messages,
        "max_completion_tokens": limit,
    }
    effort = config.get_setting("LLM_REASONING_EFFORT")
    if effort:
        payload["reasoning_effort"] = effort

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=config.get_int("LLM_TIMEOUT_SECONDS", 60),
        )
    except requests.exceptions.Timeout:
        return LLMResult(ok=False, error="The AI service took too long to answer. Please try again.")
    except requests.exceptions.RequestException:
        return LLMResult(ok=False, error="Could not reach the AI service. Check your internet connection.")

    if response.status_code != 200:
        return LLMResult(ok=False, error=_friendly_http_error(response.status_code))

    try:
        data = response.json()
        choice = data["choices"][0]
        text = (choice.get("message", {}).get("content") or "").strip()
        usage = data.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
        finish_reason = choice.get("finish_reason")
    except (ValueError, KeyError, IndexError, TypeError):
        return LLMResult(ok=False, error="The AI service sent a reply the app could not read.")

    if not text:
        if finish_reason == "length":
            return LLMResult(
                ok=False,
                error="The answer ran out of space before it was finished. Please try a shorter or simpler request.",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
        return LLMResult(ok=False, error="The AI service returned an empty answer. Please try again.")

    return LLMResult(
        ok=True,
        text=text,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )


def _friendly_http_error(status):
    if status in (401, 403):
        return "The AI service rejected the API key. Check LLM_API_KEY in the app secrets."
    if status == 402:
        return "The Aikredits for this key may be used up. Ask your instructor or teammate."
    if status == 429:
        return "The AI service is busy or the usage limit was reached. Please wait a moment and try again."
    if status >= 500:
        return "The AI service had a problem on its side. Please try again later."
    return f"The AI service returned an error (code {status})."
