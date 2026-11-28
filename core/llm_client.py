"""LLM client for LakbayLigtas AI.

Primary provider: Aiki Labs (class platform, OpenAI-compatible).
Optional backup:  a free OpenAI-compatible provider (Groq by default), used ONLY
when the primary fails because of a key, credit, rate-limit, server, or network
problem. Features call ask() and never talk to a provider directly.

Errors become friendly messages and API keys are never shown to the user.
There are no automatic retries on the same provider, because calls cost credits.
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
    provider: str = "primary"  # "primary" (Aiki Labs) or "backup"

    @property
    def used_backup(self):
        return self.provider == "backup"

    @property
    def estimated_ak(self):
        """Rough Aikredits used (1 AK is about 100 input or 20 output tokens).
        The backup provider does not use Aikredits."""
        if self.provider != "primary":
            return 0.0
        return round(self.prompt_tokens / 100 + self.completion_tokens / 20, 1)


@dataclass
class _Provider:
    name: str
    base_url: str
    model: str
    api_key: object  # str or None
    token_param: str
    send_reasoning: bool


def trim_history(history, max_messages=None):
    """Keep only the most recent messages so each call stays cheap."""
    if max_messages is None:
        max_messages = config.get_int("MAX_HISTORY_MESSAGES", 8)
    trimmed = history[-max_messages:]
    # The first message sent should be from the user.
    while trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]
    return trimmed


def _providers():
    primary = _Provider(
        name="primary",
        base_url=str(config.get_setting("LLM_BASE_URL")).rstrip("/"),
        model=config.get_setting("LLM_MODEL"),
        api_key=config.get_api_key(),
        token_param="max_completion_tokens",
        send_reasoning=True,
    )
    backup = None
    backup_key = config.get_backup_api_key()
    if backup_key:
        backup = _Provider(
            name="backup",
            base_url=str(config.get_setting("LLM_BACKUP_BASE_URL")).rstrip("/"),
            model=config.get_setting("LLM_BACKUP_MODEL"),
            api_key=backup_key,
            token_param="max_tokens",
            send_reasoning=False,
        )
    return primary, backup


def ask(messages, max_tokens=None):
    limit = max_tokens or config.get_int("LLM_MAX_OUTPUT_TOKENS", 600)
    limit = min(limit, 800)  # the course key allows at most 800

    primary, backup = _providers()
    result, can_fall_back = _call(primary, messages, limit)
    if result.ok or not can_fall_back or backup is None:
        return result

    backup_result, _ = _call(backup, messages, limit)
    if backup_result.ok:
        return backup_result
    return result  # show the primary provider's error


def _call(provider, messages, limit):
    """Call one provider. Returns (LLMResult, can_fall_back_to_backup)."""
    if not provider.api_key:
        return (
            LLMResult(
                ok=False,
                provider=provider.name,
                error="The AI service is not configured yet. Add LLM_API_KEY to the app secrets.",
            ),
            True,
        )

    payload = {
        "model": provider.model,
        "messages": messages,
        provider.token_param: limit,
    }
    effort = config.get_setting("LLM_REASONING_EFFORT")
    if provider.send_reasoning and effort:
        payload["reasoning_effort"] = effort

    try:
        response = requests.post(
            f"{provider.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {provider.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=config.get_int("LLM_TIMEOUT_SECONDS", 60),
        )
    except requests.exceptions.Timeout:
        return _fail(provider, "The AI service took too long to answer. Please try again."), True
    except requests.exceptions.RequestException:
        return _fail(provider, "Could not reach the AI service. Check your internet connection."), True

    if response.status_code != 200:
        status = response.status_code
        fallbackable = status in (401, 402, 403, 429) or status >= 500
        return _fail(provider, _friendly_http_error(status)), fallbackable

    try:
        data = response.json()
        choice = data["choices"][0]
        text = (choice.get("message", {}).get("content") or "").strip()
        usage = data.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or 0)
        completion_tokens = int(usage.get("completion_tokens") or 0)
        finish_reason = choice.get("finish_reason")
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return _fail(provider, "The AI service sent a reply the app could not read."), False

    if not text:
        if finish_reason == "length":
            message = "The answer ran out of space before it was finished. Please try a shorter or simpler request."
        else:
            message = "The AI service returned an empty answer. Please try again."
        result = _fail(provider, message)
        result.prompt_tokens = prompt_tokens
        result.completion_tokens = completion_tokens
        return result, False

    return (
        LLMResult(
            ok=True,
            text=text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            provider=provider.name,
        ),
        False,
    )


def _fail(provider, message):
    return LLMResult(ok=False, error=message, provider=provider.name)


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