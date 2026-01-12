import typing

import sulguk

from notifier.application import interfaces
from notifier.application.services import RenderService
from notifier.domain.entities import Issue, PullRequest

TG_MESSAGE_LIMIT: typing.Final = 4096

ISSUE_TEMPLATE: typing.Final = (
    "🚀 <b>New issue to <a href=/{repository}>{repository}</a> by <a href=/{user}>@{user}</a> </b><br/>"
    "📝 <b>{title}</b> (<a href='{url}'>#{id}</a>)<br/><br/>"
    "{body}<br/>"
    "{labels}"
    "{promo}"
)

PR_TEMPLATE: typing.Final = (
    "🎉 <b>New Pull Request to <a href=/{repository}>{repository}</a> by <a href=/{user}>@{user}</a></b><br/>"
    "✨ <b>{title}</b> (<a href='{url}'>#{id}</a>)<br/>"
    "📊 +{additions}/-{deletions}<br/>"
    "🌿 {head_ref} → {base_ref}<br/><br/>"
    "{body}<br/>"
    "{labels}"
    "{promo}"
)


class SendIssue:
    def __init__(
        self,
        template: str,
        github: interfaces.Github,
        telegram: interfaces.Telegram,
        render_service: RenderService,
    ) -> None:
        self._template = template or ISSUE_TEMPLATE
        self._github = github
        self._telegram = telegram
        self._render_service = render_service

    def handler(self, chat_id: str, thread_id: str | None) -> None:
        issue = self._github.get_issue()

        labels = self._render_service.format_labels(issue.labels)
        body = self._render_service.format_body(issue.body)

        message = self._create_message(issue, body, labels)

        render_result = sulguk.transform_html(
            message,
            base_url="https://github.com",
        )

        for e in render_result.entities:
            e.pop("language", None)

        tg_body=interfaces.TgPayload(
            text=render_result.text,
            entities=render_result.entities,
            disable_web_page_preview=True,
            chat_id=chat_id,
            message_thread_id=thread_id,
        )

        if len(render_result.text) <= TG_MESSAGE_LIMIT:
            return self._telegram.send_message(tg_body)

        message_without_description = self._create_message(issue, "<p></p>", labels)

        sulguk.transform_html(
            message_without_description,
            base_url="https://github.com",
        )

    def _create_message(self, issue: Issue, body: str, labels: str) -> str:
        return self._template.format(
            id=issue.id,
            user=issue.user,
            title=issue.title,
            labels=labels,
            url=issue.url,
            body=body,
            repository=issue.repository,
            promo="<a href='/reagento/relator'>sent via relator</a>",
        )


class SendPR:
    def __init__(
        self,
        template: str,
        github: interfaces.Github,
        telegram: interfaces.Telegram,
        render_service: RenderService,
    ) -> None:
        self._template = template or PR_TEMPLATE
        self._github = github
        self._telegram = telegram
        self._render_service = render_service

    def handler(self, chat_id: str, thread_id: str | None) -> None:
        pr = self._github.get_pull_request()

        labels = self._render_service.format_labels(pr.labels)
        body = self._render_service.format_body(pr.body)

        message = self._create_message(pr, body, labels)

        render_result = sulguk.transform_html(
            message,
            base_url="https://github.com",
        )

        for e in render_result.entities:
            e.pop("language", None)

        tg_body = interfaces.TgPayload(
            text=render_result.text,
            entities=render_result.entities,
            disable_web_page_preview=True,
            chat_id=chat_id,
            message_thread_id=thread_id,
        )

        if len(render_result.text) <= TG_MESSAGE_LIMIT:
            return self._telegram.send_message(tg_body)

        message_without_description = self._create_message(pr, "<p></p>", labels)

        sulguk.transform_html(
            message_without_description,
            base_url="https://github.com",
        )

    def _create_message(self, pr: PullRequest, body: str, labels: str) -> str:
        return self._template.format(
            id=pr.id,
            user=pr.user,
            title=pr.title,
            labels=labels,
            url=pr.url,
            body=body,
            repository=pr.repository,
            additions=pr.additions,
            deletions=pr.deletions,
            head_ref=pr.head_ref,
            base_ref=pr.base_ref,
            promo="<a href='/reagento/relator'>sent via relator</a>",
        )
