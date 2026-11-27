import requests

from core import config, llm_client

FAKE_KEY = "sk-test-FAKEKEY123"


class FakeResponse:
    def __init__(self, status=200, data=None):
        self.status_code = status
        self._data = data

    def json(self):
        if self._data is None:
            raise ValueError("no json")
        return self._data


def good_data(text="Hello hiker!", finish="stop", prompt=1000, completion=100):
    return {
        "choices": [{"message": {"content": text}, "finish_reason": finish}],
        "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
    }


def set_key(monkeypatch, key=FAKE_KEY):
    monkeypatch.setenv("LLM_API_KEY", key)


def test_missing_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setattr(config, "_from_file", lambda name: None)
    monkeypatch.setattr(config, "_from_streamlit", lambda name: None)
    result = llm_client.ask([{"role": "user", "content": "hi"}])
    assert result.ok is False
    assert "not configured" in result.error


def test_placeholder_key_is_treated_as_missing(monkeypatch):
    set_key(monkeypatch, "paste-real-key-later")
    assert config.get_api_key() is None


def test_success_and_request_shape(monkeypatch):
    set_key(monkeypatch)
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured.update(url=url, headers=headers, json=json, timeout=timeout)
        return FakeResponse(200, good_data())

    monkeypatch.setattr(requests, "post", fake_post)
    result = llm_client.ask([{"role": "user", "content": "hi"}])
    assert result.ok and result.text == "Hello hiker!"
    assert captured["url"].endswith("/chat/completions")
    assert captured["headers"]["Authorization"] == f"Bearer {FAKE_KEY}"
    assert captured["json"]["model"] == "gpt-6-luna"
    assert captured["json"]["max_completion_tokens"] == 600
    assert result.estimated_ak == 15.0  # 1000/100 + 100/20


def test_max_tokens_capped_at_800(monkeypatch):
    set_key(monkeypatch)
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured.update(json=json)
        return FakeResponse(200, good_data())

    monkeypatch.setattr(requests, "post", fake_post)
    llm_client.ask([{"role": "user", "content": "hi"}], max_tokens=5000)
    assert captured["json"]["max_completion_tokens"] == 800


def test_http_errors_are_friendly_and_hide_key(monkeypatch):
    set_key(monkeypatch)
    for status in (401, 402, 429, 500, 418):
        monkeypatch.setattr(requests, "post", lambda *a, s=status, **k: FakeResponse(s, {}))
        result = llm_client.ask([{"role": "user", "content": "hi"}])
        assert result.ok is False
        assert FAKE_KEY not in result.error
        assert result.error


def test_timeout_and_connection_errors(monkeypatch):
    set_key(monkeypatch)

    def raise_timeout(*a, **k):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requests, "post", raise_timeout)
    assert "too long" in llm_client.ask([{"role": "user", "content": "hi"}]).error

    def raise_conn(*a, **k):
        raise requests.exceptions.ConnectionError(FAKE_KEY)

    monkeypatch.setattr(requests, "post", raise_conn)
    result = llm_client.ask([{"role": "user", "content": "hi"}])
    assert "Could not reach" in result.error
    assert FAKE_KEY not in result.error


def test_empty_answer_due_to_length(monkeypatch):
    set_key(monkeypatch)
    monkeypatch.setattr(
        requests, "post", lambda *a, **k: FakeResponse(200, good_data(text="", finish="length"))
    )
    result = llm_client.ask([{"role": "user", "content": "hi"}])
    assert result.ok is False
    assert "ran out of space" in result.error


def test_unreadable_response(monkeypatch):
    set_key(monkeypatch)
    monkeypatch.setattr(requests, "post", lambda *a, **k: FakeResponse(200, {"oops": 1}))
    assert "could not read" in llm_client.ask([{"role": "user", "content": "hi"}]).error


def test_trim_history_keeps_recent_and_starts_with_user():
    history = []
    for i in range(6):
        history.append({"role": "user", "content": f"u{i}"})
        history.append({"role": "assistant", "content": f"a{i}"})
    trimmed = llm_client.trim_history(history, max_messages=5)
    assert len(trimmed) <= 5
    assert trimmed[0]["role"] == "user"
    assert trimmed[-1]["content"] == "a5"
