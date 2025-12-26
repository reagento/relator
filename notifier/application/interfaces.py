import abc
from dataclasses import dataclass
import typing

import sulguk

from notifier.domain.entities import PullRequest, Issue

@dataclass
class TgPayload:
    text: str
    entities: list[sulguk.data.MessageEntity]
    disable_web_page_preview: bool
    chat_id: str
    message_thread_id: str | None


class Github(typing.Protocol):
    @abc.abstractmethod
    def get_issue(self) -> Issue: ...

    @abc.abstractmethod
    def get_pull_request(self) -> PullRequest: ...


class Telegram(typing.Protocol):
    @abc.abstractmethod
    def send_message(self, body: TgPayload) -> None: ...
