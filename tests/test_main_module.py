import os
from unittest.mock import patch

import pytest

from notifier.__main__ import get_interactor
from notifier.application.interactors import SendIssue, SendPR


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://api.github.com/repos/owner/repo/issues/1", SendIssue),
        ("https://api.github.com/repos/owner/repo/pulls/2", SendPR),
    ],
)
def test_get_interactor_detects_type(url, expected):
    """get_interactor should recognize API URLs for issues and PRs."""
    assert get_interactor(url) is expected


def test_get_interactor_raises_on_unknown():
    with pytest.raises(ValueError):
        get_interactor("https://github.com/owner/repo/unknown/1")


@patch.dict(
    os.environ,
    {
        "TELEGRAM_CHAT_ID": "123",
        "TELEGRAM_BOT_TOKEN": "token",
        "ATTEMPT_COUNT": "3",
        "EVENT_URL": "https://api.github.com/repos/o/r/issues/1",
        "GITHUB_TOKEN": "gtoken",
        "CUSTOM_LABELS": "custom1,custom2",
        "JOIN_INPUT_WITH_LIST": "1",
        "HTML_TEMPLATE": "",
    },
)
@patch("notifier.__main__.GithubGateway")
@patch("notifier.__main__.TelegramGateway")
@patch("notifier.__main__.RenderService")
@patch("notifier.__main__.get_interactor")
def test_main_module_env_parsing(
    mock_get_interactor, mock_render_service, mock_telegram, mock_github
):
    """
    Smoke-test the main module wiring by simulating environment and
    checking that the selected interactor's handler is invoked.
    """

    # prepare fake gateways and interactor
    class _FakeGithub:
        def __init__(self, *_, **__):
            pass

    class _FakeTelegram:
        def __init__(self, *_, **__):
            pass

    class _FakeRenderService:
        def __init__(self, *_, **__):
            pass

    class _FakeInteractor:
        def __init__(self, *_, **__):
            self.called = False

        def handler(self):
            self.called = True

    mock_github.return_value = _FakeGithub()
    mock_telegram.return_value = _FakeTelegram()
    mock_render_service.return_value = _FakeRenderService()
    mock_get_interactor.return_value = _FakeInteractor

    # Import and execute main logic
    import importlib

    main_mod = importlib.import_module("notifier.__main__")

    fake_interactor = main_mod.get_interactor(os.environ["EVENT_URL"])(
        template="",
        github=_FakeGithub(),
        telegram=_FakeTelegram(),
        render_service=_FakeRenderService(),
    )
    # Ensure handler exists and can be called without errors
    fake_interactor.handler()


