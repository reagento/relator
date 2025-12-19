from unittest.mock import Mock, patch

import requests
import sulguk

from notifier.infrastructure.github_gateway import GithubGateway
from notifier.infrastructure.telegram_gateway import TelegramGateway


@patch("notifier.infrastructure.github_gateway.requests.get")
def test_github_gateway_get_issue_uses_expected_headers(mock_get):
    response = Mock()
    response.json.return_value = {
        "number": 1,
        "title": "Issue",
        "labels": [{"name": "bug"}],
        "html_url": "https://github.com/owner/repo/issues/1",
        "user": {"login": "user"},
        "body_html": "<p>body</p>",
    }
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    gw = GithubGateway(token="TOKEN", event_url="https://api.github.com/issue")
    issue = gw.get_issue()

    mock_get.assert_called_once_with(
        "https://api.github.com/issue",
        headers={
            "Accept": "application/vnd.github.v3.html+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": "Bearer TOKEN",
        },
        timeout=30,
    )
    assert issue.title == "Issue"
    assert issue.labels == ["bug"]
    assert issue.user == "user"
    assert issue.url == "https://github.com/owner/repo/issues/1"
    assert issue.body == "<p>body</p>"


@patch("notifier.infrastructure.github_gateway.requests.get")
def test_github_gateway_get_pull_request_builds_entity(mock_get):
    response = Mock()
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
    mock_get.return_value = response

    gw = GithubGateway(token="TOKEN", event_url="https://api.github.com/pr")
    pr = gw.get_pull_request()

    assert pr.id == 2
    assert pr.additions == 5
    assert pr.deletions == 1
    assert pr.repository == "owner/repo"


@patch("notifier.infrastructure.telegram_gateway.requests.post")
def test_telegram_gateway_send_message_success(mock_post, capsys):
    result = sulguk.RenderResult(text="hi", entities=[{"offset": 0, "length": 2, "type": "bold"}])

    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {"ok": True}
    mock_post.return_value = response

    gw = TelegramGateway(
        chat_id="123",
        bot_token="TOKEN",
        attempt_count=1,
        message_thread_id=None,
    )

    gw.send_message(result)

    mock_post.assert_called_once()
    call_args, call_kwargs = mock_post.call_args
    assert "sendMessage" in call_args[0]
    assert call_kwargs["json"]["text"] == "hi"
    # language field should be removed if exists
    for e in call_kwargs["json"]["entities"]:
        assert "language" not in e

    captured = capsys.readouterr()
    # Should print response json on success
    assert "ok" in captured.out


@patch("notifier.infrastructure.telegram_gateway.time.sleep")
@patch("notifier.infrastructure.telegram_gateway.requests.post")
def test_telegram_gateway_send_message_retries_on_error(mock_post, mock_sleep, capsys):
    result = sulguk.RenderResult(text="hi", entities=[])

    response = Mock()
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("fail")
    response.content = b"error"
    mock_post.return_value = response

    gw = TelegramGateway(
        chat_id="123",
        bot_token="TOKEN",
        attempt_count=3,
        message_thread_id="456",
    )

    gw.send_message(result)

    # ensure we retried attempt_count times
    assert mock_post.call_count == 3
    captured = capsys.readouterr()
    assert "error" in captured.err


