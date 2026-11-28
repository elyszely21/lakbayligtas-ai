"""Tests for the free backup provider. The network is faked, so no credits are used."""

import requests

from core import llm_client

PRIMARY_KEY = "sk-test-PRIMARYKEY"
BACKUP_KEY = "gsk-test-BACKUPKEY"


class FakeResponse:
    def __init__(self, status=200, data=None):
        self.status_code = status
        self._data = data

    def json(self):
        if self._data is None:
            raise ValueError("no json")
        return self._data


def good(text="Hello hiker!"):
    return {
        "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1000, "completion_tokens": 100},
    }


def setup_keys(monkeypatch, primary=True, backup=True):
    if primary:
        monkeypatch.setenv("LLM_API_KEY", PRIMARY_KEY)
    if backup:
        monkeypatch.setenv("LLM_BACKUP_API_KEY", BACKUP_KEY)


def fake_post_factory(primary_response, backup_response, calls):
    def fake_post(url, headers, json, timeout):
        calls.append({"url": url, "headers": headers, "json": json})
        if "aiki-labs" in url:
            if isinstance(primary_response, Exception):
                raise primary_response
            return primary_response
        return backup_response

    return fake_post


MSG = [{"role": "user", "content": "hi"}]


def test_primary_ok_does_not_call_backup(monkeypatch):
    setup_keys(monkeypatch)
    calls = []
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(200, good()), FakeResponse(200, good("backup")), calls))
    result = llm_client.ask(MSG)
    assert result.ok and result.provider == "primary" and not result.used_backup
    assert len(calls) == 1


def test_fallback_on_http_errors(monkeypatch):
    for status in (401, 402, 429, 500, 503):
        setup_keys(monkeypatch)
        calls = []
        monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(status, {}), FakeResponse(200, good("from backup")), calls))
        result = llm_client.ask(MSG)
        assert result.ok and result.used_backup and result.text == "from backup", status
        assert len(calls) == 2


def test_fallback_on_timeout_and_connection_error(monkeypatch):
    for error in (requests.exceptions.Timeout(), requests.exceptions.ConnectionError()):
        setup_keys(monkeypatch)
        calls = []
        monkeypatch.setattr(requests, "post", fake_post_factory(error, FakeResponse(200, good("from backup")), calls))
        result = llm_client.ask(MSG)
        assert result.ok and result.used_backup


def test_backup_request_shape_and_keys_not_mixed(monkeypatch):
    setup_keys(monkeypatch)
    calls = []
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(429, {}), FakeResponse(200, good()), calls))
    llm_client.ask(MSG, max_tokens=500)
    primary_call, backup_call = calls
    assert primary_call["headers"]["Authorization"] == f"Bearer {PRIMARY_KEY}"
    assert primary_call["json"]["max_completion_tokens"] == 500
    assert backup_call["headers"]["Authorization"] == f"Bearer {BACKUP_KEY}"
    assert "groq" in backup_call["url"]
    assert backup_call["json"]["max_tokens"] == 500
    assert "reasoning_effort" not in backup_call["json"]
    assert PRIMARY_KEY not in str(backup_call)


def test_backup_uses_no_aikredits(monkeypatch):
    setup_keys(monkeypatch)
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(429, {}), FakeResponse(200, good()), []))
    assert llm_client.ask(MSG).estimated_ak == 0.0


def test_missing_primary_key_uses_backup(monkeypatch):
    setup_keys(monkeypatch, primary=False)
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(200, good()), FakeResponse(200, good("from backup")), []))
    result = llm_client.ask(MSG)
    assert result.ok and result.used_backup


def test_no_backup_returns_primary_error(monkeypatch):
    setup_keys(monkeypatch, backup=False)
    calls = []
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(429, {}), FakeResponse(200, good()), calls))
    result = llm_client.ask(MSG)
    assert result.ok is False and len(calls) == 1


def test_both_fail_returns_primary_error_without_keys(monkeypatch):
    setup_keys(monkeypatch)
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(402, {}), FakeResponse(500, {}), []))
    result = llm_client.ask(MSG)
    assert result.ok is False and "Aikredits" in result.error
    assert PRIMARY_KEY not in result.error and BACKUP_KEY not in result.error


def test_no_fallback_when_answer_is_empty_or_unreadable(monkeypatch):
    setup_keys(monkeypatch)
    calls = []
    empty = {"choices": [{"message": {"content": ""}, "finish_reason": "length"}], "usage": {}}
    monkeypatch.setattr(requests, "post", fake_post_factory(FakeResponse(200, empty), FakeResponse(200, good()), calls))
    result = llm_client.ask(MSG)
    assert result.ok is False and len(calls) == 1