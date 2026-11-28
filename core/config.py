"""Settings loader for LakbayLigtas AI.

Looks for each setting in this order:
1. Environment variables (Streamlit Community Cloud also exposes its Secrets this way)
2. The local file .streamlit/secrets.toml (never committed to GitHub)
3. st.secrets (only if Streamlit is available)
4. The default value below

The API key has NO default, so it can never be written into source code.
"""

import os
import tomllib
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SECRETS_FILE = _ROOT / ".streamlit" / "secrets.toml"

DEFAULTS = {
    "LLM_BASE_URL": "https://aiki-labs.up.railway.app/api/v1",
    "LLM_MODEL": "gpt-6-luna",
    "LLM_MAX_OUTPUT_TOKENS": "600",   # course key allows at most 800
    "LLM_REASONING_EFFORT": "low",    # keeps hidden reasoning (and cost) small
    "LLM_TIMEOUT_SECONDS": "60",
    "MAX_USER_MESSAGES": "15",        # per browser session, protects shared credits
    "MAX_HISTORY_MESSAGES": "8",      # older messages are not re-sent
    # Free backup provider (OpenAI-compatible). Used only if Aiki Labs fails.
    "LLM_BACKUP_BASE_URL": "https://api.groq.com/openai/v1",
    "LLM_BACKUP_MODEL": "llama-3.3-70b-versatile",  # confirm in your Groq console
}

_PLACEHOLDER_HINTS = ("paste", "your-key", "changeme", "xxxx")


def _from_file(name):
    try:
        with open(_SECRETS_FILE, "rb") as f:
            return tomllib.load(f).get(name)
    except (FileNotFoundError, tomllib.TOMLDecodeError, OSError):
        return None


def _from_streamlit(name):
    try:
        import streamlit as st

        return st.secrets.get(name)
    except Exception:
        return None


def get_setting(name, default=None):
    value = os.environ.get(name)
    if value is None:
        value = _from_file(name)
    if value is None:
        value = _from_streamlit(name)
    if value is None:
        value = DEFAULTS.get(name, default)
    return value


def get_int(name, default=0):
    try:
        return int(get_setting(name, default))
    except (TypeError, ValueError):
        return int(default)


def _clean_key(name):
    """Return the named key, or None if it is missing or still a placeholder."""
    key = get_setting(name)
    if not key or not str(key).strip():
        return None
    key = str(key).strip()
    if any(hint in key.lower() for hint in _PLACEHOLDER_HINTS):
        return None
    return key


def get_api_key():
    """Aiki Labs key (primary provider)."""
    return _clean_key("LLM_API_KEY")


def get_backup_api_key():
    """Free backup provider key (optional)."""
    return _clean_key("LLM_BACKUP_API_KEY")