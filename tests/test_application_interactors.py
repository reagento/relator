import sulguk

from notifier.application.interactors import (
    ISSUE_TEMPLATE,
    PR_TEMPLATE,
    SendIssue,
    SendPR,
    TG_MESSAGE_LIMIT,
)
from notifier.application.services import RenderService
from notifier.domain.entities import Issue, PullRequest


class _GithubStub:
    def __init__(self, issue: Issue | None = None, pr: PullRequest | None = None):
        self._issue = issue or Issue(
            id=1,
            title="Issue title",
            labels=[],
            url="https://github.com/owner/repo/issues/1",
            user="user",
            body="body",
        )
        self._pr = pr or PullRequest(
            id=1,
            title="PR title",
            labels=[],
            url="https://github.com/owner/repo/pull/1",
            user="user",
            body="body",
            additions=1,
            deletions=0,
            head_ref="feature",
            base_ref="main",
            repository="owner/repo",
        )

    def get_issue(self) -> Issue:
        return self._issue

    def get_pull_request(self) -> PullRequest:
        return self._pr


class _TelegramStub:
    def __init__(self):
        self.sent: list[sulguk.RenderResult] = []

    def send_message(self, render_result: sulguk.RenderResult) -> None:
        self.sent.append(render_result)


class _RenderServiceStub(RenderService):
    def __init__(self, labels: str = "#bug", body: str = "<p>body</p>"):
        super().__init__(custom_labels=[], join_input_with_list=False)
        self._labels = labels
        self._body = body

    def format_labels(self, labels: list[str]):
        return self._labels

    def format_body(self, body: str) -> str:
        return self._body


def _make_render_result(text: str) -> sulguk.RenderResult:
    # Minimal object compatible with what TelegramGateway expects
    return sulguk.RenderResult(
        text=text,
        entities=[],
    )


def test_send_issue_uses_default_template(monkeypatch):
    github = _GithubStub()
    telegram = _TelegramStub()
    render_service = _RenderServiceStub()

    # capture input HTML passed to sulguk.transform_html
    captured = {}

    def _fake_transform_html(message: str, base_url: str):
        captured["message"] = message
        return _make_render_result("rendered")

    monkeypatch.setattr("notifier.application.interactors.sulguk.transform_html", _fake_transform_html)

    interactor = SendIssue(
        template="",
        github=github,
        telegram=telegram,
        render_service=render_service,
    )

    interactor.handler()

    assert ISSUE_TEMPLATE.format(
        id=github.get_issue().id,
        user=github.get_issue().user,
        title=github.get_issue().title,
        labels=render_service._labels,
        url=github.get_issue().url,
        body=render_service._body,
        repository=github.get_issue().repository,
        promo="<a href='/reagento/relator'>sent via relator</a>",
    ) == captured["message"]
    # ensure telegram was called with rendered result
    assert len(telegram.sent) == 1
    assert telegram.sent[0].text == "rendered"


def test_send_issue_truncates_long_messages(monkeypatch):
    github = _GithubStub()
    telegram = _TelegramStub()
    # create very long body
    long_body = "x" * (TG_MESSAGE_LIMIT + 10)
    render_service = _RenderServiceStub(body=long_body)

    # first call returns too-long message, second call shorter text
    calls: list[str] = []

    def _fake_transform_html(message: str, base_url: str):
        calls.append(message)
        # render_result.text should reflect the original message length
        return _make_render_result(text=message)

    monkeypatch.setattr("notifier.application.interactors.sulguk.transform_html", _fake_transform_html)

    interactor = SendIssue(
        template=ISSUE_TEMPLATE,
        github=github,
        telegram=telegram,
        render_service=render_service,
    )

    interactor.handler()

    # when message length exceeds limit, we do not send via telegram
    assert telegram.sent == []
    # second transform_html call should be without description
    assert len(calls) == 2
    assert "<p></p>" in calls[1]


def test_send_pr_uses_default_template(monkeypatch):
    github = _GithubStub()
    telegram = _TelegramStub()
    render_service = _RenderServiceStub()

    captured = {}

    def _fake_transform_html(message: str, base_url: str):
        captured["message"] = message
        return _make_render_result("rendered")

    monkeypatch.setattr("notifier.application.interactors.sulguk.transform_html", _fake_transform_html)

    interactor = SendPR(
        template="",
        github=github,
        telegram=telegram,
        render_service=render_service,
    )

    interactor.handler()

    pr = github.get_pull_request()
    expected_message = PR_TEMPLATE.format(
        id=pr.id,
        user=pr.user,
        title=pr.title,
        labels=render_service._labels,
        url=pr.url,
        body=render_service._body,
        repository=pr.repository,
        additions=pr.additions,
        deletions=pr.deletions,
        head_ref=pr.head_ref,
        base_ref=pr.base_ref,
        promo="<a href='/reagento/relator'>sent via relator</a>",
    )
    assert captured["message"] == expected_message
    assert len(telegram.sent) == 1
    assert telegram.sent[0].text == "rendered"


def test_send_pr_truncates_long_messages(monkeypatch):
    github = _GithubStub()
    telegram = _TelegramStub()
    long_body = "x" * (TG_MESSAGE_LIMIT + 10)
    render_service = _RenderServiceStub(body=long_body)

    calls: list[str] = []

    def _fake_transform_html(message: str, base_url: str):
        calls.append(message)
        return _make_render_result(text=message)

    monkeypatch.setattr("notifier.application.interactors.sulguk.transform_html", _fake_transform_html)

    interactor = SendPR(
        template=PR_TEMPLATE,
        github=github,
        telegram=telegram,
        render_service=render_service,
    )

    interactor.handler()

    assert telegram.sent == []
    assert len(calls) == 2
    assert "<p></p>" in calls[1]


