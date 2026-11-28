"""Keeps every test independent of your real secrets and environment."""

import pytest

from core import config


@pytest.fixture(autouse=True)
def isolate_config(monkeypatch):
    for name in ("LLM_API_KEY", "LLM_BACKUP_API_KEY", "LLM_BACKUP_BASE_URL", "LLM_BACKUP_MODEL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(config, "_from_file", lambda name: None)
    monkeypatch.setattr(config, "_from_streamlit", lambda name: None)