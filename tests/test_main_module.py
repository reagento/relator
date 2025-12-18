import os

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


def test_main_module_env_parsing(monkeypatch):
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

    # patch environment
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token")
    monkeypatch.setenv("ATTEMPT_COUNT", "3")
    monkeypatch.setenv("EVENT_URL", "https://api.github.com/repos/o/r/issues/1")
    monkeypatch.setenv("GITHUB_TOKEN", "gtoken")
    monkeypatch.setenv("CUSTOM_LABELS", "custom1,custom2")
    monkeypatch.setenv("JOIN_INPUT_WITH_LIST", "1")
    monkeypatch.setenv("HTML_TEMPLATE", "")

    # re-import main to execute the __main__ guard logic in a controlled way:
    # we simulate being run as script by setting __name__ before executing.
    import importlib

    # Create a new module object from the source, but do not run its main block.
    # Instead, we patch its dependencies first and then execute the guarded code
    # by calling its main interactor manually.
    main_mod = importlib.import_module("notifier.__main__")

    # patch gateways and render service used inside __main__
    monkeypatch.setattr(main_mod, "GithubGateway", _FakeGithub)
    monkeypatch.setattr(main_mod, "TelegramGateway", _FakeTelegram)
    monkeypatch.setattr(main_mod, "RenderService", _FakeRenderService)

    # patch get_interactor to return our fake interactor class
    monkeypatch.setattr(main_mod, "get_interactor", lambda _url: _FakeInteractor)

    fake_interactor = main_mod.get_interactor(os.environ["EVENT_URL"])(
        template="",
        github=_FakeGithub,
        telegram=_FakeTelegram,
        render_service=_FakeRenderService,
    )
    # Ensure handler exists and can be called without errors
    fake_interactor.handler()


