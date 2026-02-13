import typing
from datetime import datetime, timezone

import bs4
from markdownify import markdownify

from notifier.application import interfaces
from notifier.domain.entities import Issue, PullRequest
from notifier.infrastructure.send_weebhook import send_webhook

DISCORD_EMBED_DESC_LIMIT: typing.Final = 2000
DISCORD_COLOR_ISSUE: typing.Final = 0x28A745  # green
DISCORD_COLOR_PR: typing.Final = 0x6F42C1  # purple


class DiscordGateway(interfaces.Notifier):
    def __init__(
        self,
        webhook_url: str,
        attempt_count: int,
    ) -> None:
        self._webhook_url = webhook_url
        self._attempt_count = attempt_count

    def send_issue(
        self,
        issue: Issue,
        formatted_body: str,
        formatted_labels: str,
    ) -> None:
        embed = self._format_issue(issue, formatted_body, formatted_labels)
        send_webhook(
            url=self._webhook_url,
            payload={"embeds": [embed]},
            attempts=self._attempt_count,
        )

    def send_pull_request(
        self,
        pull_request: PullRequest,
        formatted_body: str,
        formatted_labels: str,
    ) -> None:
        embed = self._format_pull_request(
            pull_request, formatted_body, formatted_labels
        )
        send_webhook(
            url=self._webhook_url,
            payload={"embeds": [embed]},
            attempts=self._attempt_count,
        )

    def _format_issue(
        self, issue: Issue, body: str, labels: str
    ) -> dict[str, typing.Any]:
        markdown_body = self._html_to_markdown(body)
        description = self._create_description(markdown_body, labels)

        embed = {
            "title": f"🚀 New Issue #{issue.id}: {self._truncate_title(issue.title)}",
            "description": description,
            "url": issue.url,
            "color": DISCORD_COLOR_ISSUE,
            "author": {
                "name": f"@{issue.user}",
                "url": f"https://github.com/{issue.user}",
                "icon_url": f"https://github.com/{issue.user}.png?size=32",
            },
            "fields": [
                {
                    "name": "Repository",
                    "value": f"[{issue.repository}](https://github.com/{issue.repository})",
                    "inline": True,
                },
                {
                    "name": "Issue Number",
                    "value": f"#{issue.id}",
                    "inline": True,
                },
            ],
            "footer": {
                "text": "sent via relator",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return embed

    def _format_pull_request(
        self, pr: PullRequest, body: str, labels: str
    ) -> dict[str, typing.Any]:
        labels = labels.rstrip("<br/>")
        markdown_body = self._html_to_markdown(body)
        description = self._create_description(markdown_body, labels)

        embed = {
            "title": f"🎉 New PR #{pr.id}: {self._truncate_title(pr.title)}",
            "description": description,
            "url": pr.url,
            "color": DISCORD_COLOR_PR,
            "author": {
                "name": f"@{pr.user}",
                "url": f"https://github.com/{pr.user}",
                "icon_url": f"https://github.com/{pr.user}.png?size=32",
            },
            "fields": [
                {
                    "name": "Repository",
                    "value": f"[{pr.repository}](https://github.com/{pr.repository})",
                    "inline": True,
                },
                {
                    "name": "PR Number",
                    "value": f"#{pr.id}",
                    "inline": True,
                },
                {
                    "name": "Changes",
                    "value": f"+{pr.additions} / -{pr.deletions}",
                    "inline": True,
                },
                {
                    "name": "Branch",
                    "value": f"`{pr.head_ref}` → `{pr.base_ref}`",
                    "inline": False,
                },
            ],
            "footer": {
                "text": "sent via relator",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return embed

    def _html_to_markdown(self, html: str) -> str:
        if not html or html == "<p></p>":
            return ""

        html = html.replace("<br/>", "\n")
        print(f"After trim {html=}")
        try:
            markdown = markdownify(
                html,
                heading_style="ATX",
                bullets="-",
                strip=["script", "style"],
            )
            markdown = self._clean_markdown(markdown)
            return markdown.strip()
        except Exception:
            soup = bs4.BeautifulSoup(html, "lxml")
            return soup.get_text().strip()

    def _clean_markdown(self, markdown: str) -> str:
        lines = markdown.split("\n")
        cleaned_lines = []
        empty_count = 0

        for line in lines:
            if line.strip() == "":
                empty_count += 1
                if empty_count <= 2:
                    cleaned_lines.append(line)
            else:
                empty_count = 0
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _create_description(self, markdown_body: str, labels: str) -> str:
        labels_text = f"\n\n{labels}" if labels.strip() else ""
        reserved_for_labels = len(labels_text) + 100
        available_for_body = DISCORD_EMBED_DESC_LIMIT - reserved_for_labels

        if len(markdown_body) > available_for_body:
            truncated_body = markdown_body[: available_for_body - 4] + "..."
        else:
            truncated_body = markdown_body

        description = truncated_body + labels_text

        if len(description) > DISCORD_EMBED_DESC_LIMIT:
            description = description[: DISCORD_EMBED_DESC_LIMIT - 3] + "..."

        return description

    def _truncate_title(self, title: str, max_length: int = 200) -> str:
        if len(title) <= max_length:
            return title
        return title[: max_length - 3] + "..."
