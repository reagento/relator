import os
import re
import sys

from notifier.application.interactors import SendIssue, SendPR
from notifier.application.services import RenderService
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
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]

    attempt_count = os.environ["ATTEMPT_COUNT"]

    telegram_gateway = TelegramGateway(bot_token, int(attempt_count))

    gh_token = os.environ["GITHUB_TOKEN"]

    github_gateway = GithubGateway(gh_token)

    custom_labels = os.environ.get("CUSTOM_LABELS", "").split(",")
    if custom_labels == [""]:
        custom_labels = []

    render_service = RenderService(
        custom_labels=custom_labels,
        join_input_with_list=os.environ.get("JOIN_INPUT_WITH_LIST") == "1",
    )

    event_url = os.environ["EVENT_URL"]

    html_template = os.environ.get("HTML_TEMPLATE", "").strip()

    interactor = get_interactor(event_url)(
        bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        chat_id=os.environ["TELEGRAM_CHAT_ID"],
        thread_id=os.environ.get("TELEGRAM_MESSAGE_THREAD_ID"),
        template=html_template,
        github=github_gateway,
        telegram=telegram_gateway,
        render_service=render_service,
    )

    try:
        interactor.handler()
    except Exception as e:
        print(f"Error processing event: {e}", file=sys.stderr)
        sys.exit(1)
