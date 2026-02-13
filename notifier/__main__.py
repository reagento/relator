import os
import re
import sys
import traceback

from notifier.application.interactors import SendIssue, SendPR
from notifier.application.interfaces import Notifier
from notifier.application.services import RenderService
from notifier.infrastructure.discord_gateway import DiscordGateway
from notifier.infrastructure.github_gateway import GithubGateway
from notifier.infrastructure.telegram_gateway import TelegramGateway


def get_interactor(url: str) -> type[SendIssue] | type[SendPR]:
    issue_pattern = (
        r"https://(?:api\.)?github\.com/repos/[\w\-\.]+/[\w\-\.]+/issues/\d+"
    )

    pr_pattern = r"https://(?:api\.)?github\.com/repos/[\w\-\.]+/[\w\-\.]+/pulls/\d+"

    if re.match(issue_pattern, url):
        return SendIssue
    elif re.match(pr_pattern, url):
        return SendPR
    else:
        raise ValueError(f"Unknown event type for URL: {url}")


if __name__ == "__main__":
    event_url = os.environ["EVENT_URL"]

    github_gateway = GithubGateway(
        token=(os.environ.get("GITHUB_TOKEN") or "").strip(),
        event_url=event_url,
    )

    custom_labels = os.environ.get("CUSTOM_LABELS", "").split(",")
    if custom_labels == [""]:
        custom_labels = []

    render_service = RenderService(
        custom_labels=custom_labels,
        join_input_with_list=os.environ.get("JOIN_INPUT_WITH_LIST") == "1",
    )

    notifiers: list[Notifier] = []

    tg_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if tg_bot_token and tg_chat_id:
        html_template = os.environ.get("HTML_TEMPLATE", "").strip()
        telegram_gateway = TelegramGateway(
            chat_id=tg_chat_id,
            bot_token=tg_bot_token,
            attempt_count=int(os.environ.get("ATTEMPT_COUNT", "2")),
            message_thread_id=os.environ.get("TELEGRAM_MESSAGE_THREAD_ID"),
            custom_template=html_template,
        )
        notifiers.append(telegram_gateway)

    discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if discord_webhook_url:
        discord_gateway = DiscordGateway(
            webhook_url=discord_webhook_url,
            attempt_count=int(os.environ.get("ATTEMPT_COUNT", "2")),
        )
        notifiers.append(discord_gateway)

    if not notifiers:
        print(
            "Error: No notification platform configured. "
            "Please provide either TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID or DISCORD_WEBHOOK_URL",
            file=sys.stderr,
        )
        sys.exit(1)

    interactor = get_interactor(event_url)(
        github=github_gateway,
        notifiers=notifiers,
        render_service=render_service,
    )

    try:
        interactor.handler()
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        print(f"Error processing event: {e}", file=sys.stderr)
        sys.exit(1)
