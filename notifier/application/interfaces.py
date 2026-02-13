import abc
import typing

from notifier.domain.entities import Issue, PullRequest


class Github(typing.Protocol):
    @abc.abstractmethod
    def get_issue(self) -> Issue: ...

    @abc.abstractmethod
    def get_pull_request(self) -> PullRequest: ...


class Notifier(typing.Protocol):
    @abc.abstractmethod
    def send_issue(
        self,
        issue: Issue,
        formatted_body: str,
        formatted_labels: str,
    ) -> None: ...

    @abc.abstractmethod
    def send_pull_request(
        self,
        pull_request: PullRequest,
        formatted_body: str,
        formatted_labels: str,
    ) -> None: ...
