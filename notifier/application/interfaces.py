import abc
import typing

from notifier.domain.entities import PullRequest, Issue
from notifier.infrastructure.telegram_gateway import TgPayload


class Github(typing.Protocol):
    @abc.abstractmethod
    def get_issue(self) -> Issue: ...

    @abc.abstractmethod
    def get_pull_request(self) -> PullRequest: ...


class Telegram(typing.Protocol):
    @abc.abstractmethod
    def send_message(self, body: TgPayload) -> typing.Any: ...
