from unittest import mock

import requests
import sulguk

from notifier.infrastructure.github_gateway import GithubGateway
from notifier.infrastructure.telegram_gateway import TelegramGateway


def test_github_gateway_get_issue_uses_expected_headers(monkeypatch):
    response = mock.Mock()
    response.json.return_value = {
        "number": 1,
        "title": "Issue",
        "labels": [{"name": "bug"}],
        "html_url": "https://github.com/owner/repo/issues/1",
        "user": {"login": "user"},
        "body_html": "<p>body</p>",
    }
    response.raise_for_status.return_value = None

    called_kwargs = {}

    def _fake_get(url, headers, timeout):
        called_kwargs["url"] = url
        called_kwargs["headers"] = headers
        called_kwargs["timeout"] = timeout
        return response

    monkeypatch.setattr(requests, "get", _fake_get)

    gw = GithubGateway(token="TOKEN", event_url="https://api.github.com/issue")
    issue = gw.get_issue()

    assert called_kwargs["url"] == "https://api.github.com/issue"
    assert called_kwargs["headers"]["Authorization"] == "Bearer TOKEN"
    assert called_kwargs["timeout"] == 30
    assert issue.title == "Issue"
    assert issue.labels == ["bug"]
    assert issue.user == "user"
    assert issue.url == "https://github.com/owner/repo/issues/1"
    assert issue.body == "<p>body</p>"


def test_github_gateway_get_pull_request_builds_entity(monkeypatch):
    response = mock.Mock()
    response.json.return_value = {
        "number": 2,
        "title": "PR",
        "labels": [{"name": "enhancement"}],
        "html_url": "https://github.com/owner/repo/pull/2",
        "user": {"login": "user"},
        "body_html": "<p>body</p>",
        "additions": 5,
        "deletions": 1,
        "head": {"label": "feature", "ref": "feature"},
        "base": {"ref": "main", "repo": {"full_name": "owner/repo"}},
    }
    response.raise_for_status.return_value = None

    def _fake_get(url, headers, timeout):
        return response

    monkeypatch.setattr(requests, "get", _fake_get)

    gw = GithubGateway(token="TOKEN", event_url="https://api.github.com/pr")
    pr = gw.get_pull_request()

    assert pr.id == 2
    assert pr.additions == 5
    assert pr.deletions == 1
    assert pr.repository == "owner/repo"


def test_telegram_gateway_send_message_success(monkeypatch, capsys):
    result = sulguk.RenderResult(text="hi", entities=[{"offset": 0, "length": 2, "type": "bold"}])

    response = mock.Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"ok": True}

    def _fake_post(url, json, timeout):
        assert "sendMessage" in url
        assert json["text"] == "hi"
        # language field should be removed if exists
        for e in json["entities"]:
            assert "language" not in e
        return response

    monkeypatch.setattr(requests, "post", _fake_post)

    gw = TelegramGateway(
        chat_id="123",
        bot_token="TOKEN",
        attempt_count=1,
        message_thread_id=None,
    )

    gw.send_message(result)
    captured = capsys.readouterr()
    # Should print response json on success
    assert "ok" in captured.out


def test_telegram_gateway_send_message_retries_on_error(monkeypatch, capsys):
    result = sulguk.RenderResult(text="hi", entities=[])

    response = mock.Mock()
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("fail")
    response.content = b"error"

    calls = {"count": 0}

    def _fake_post(url, json, timeout):
        calls["count"] += 1
        return response

    monkeypatch.setattr(requests, "post", _fake_post)

    # avoid real sleeping in tests
    monkeypatch.setattr("notifier.infrastructure.telegram_gateway.time.sleep", lambda *_: None)

    gw = TelegramGateway(
        chat_id="123",
        bot_token="TOKEN",
        attempt_count=3,
        message_thread_id="456",
    )

    gw.send_message(result)

    # ensure we retried attempt_count times
    assert calls["count"] == 3
    captured = capsys.readouterr()
    assert "error" in captured.err


