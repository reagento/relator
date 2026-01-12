import os
from typing import Any

from adaptix import P, Retort, loader, name_mapping, Chain
from descanso import RestBuilder
from descanso import request_transformers as rt
from descanso.http.requests import RequestsClient
from requests import Session

from notifier.application import interfaces
from notifier.domain.entities import Issue, PullRequest


def body_pre_loader(data: dict[str, Any]) -> dict[str, Any]:
    if "body_html" not in data:
        data["body_html"] = ""
    return data


issue_recipe = [
    name_mapping(
        Issue,
        map={
            "id": "number",
            "url": "html_url",
            "user": ["user", "login"],
            "body": "body_html",
        },
    ),
    loader(P[Issue], body_pre_loader, Chain.FIRST),
    loader(P[Issue].labels, lambda labels: [label["name"] for label in labels]),
]

pr_recipe = [
    name_mapping(
        PullRequest,
        map={
            "id": "number",
            "url": "html_url",
            "user": ["user", "login"],
            "head_ref": ["head", "label"],
            "base_ref": ["base", "ref"],
            "repository": ["base", "repo", "full_name"],
            "body": "body_html",
        },
    ),
    loader(P[PullRequest], body_pre_loader, Chain.FIRST),
    loader(P[PullRequest].labels, lambda labels: [label["name"] for label in labels]),
]

gh_recipe = [
    *issue_recipe,
    *pr_recipe,

]

rest = RestBuilder(
    request_body_dumper=Retort(),
    response_body_loader=Retort(recipe=gh_recipe),
    query_param_dumper=Retort(),
)


class GithubGateway(RequestsClient, interfaces.Github):
    def __init__(
        self,
        token: str,
        event_url: str,
        session: Session | None = None
    ) -> None:
        self._token = token
        self._event_url = event_url
        super().__init__(
            "",
            session or Session(),
            (
                rt.Header("Accept", "application/vnd.github.v3.html+json"),
                rt.Header("X-GitHub-Api-Version", "2022-11-28"),
                rt.Header("Authorization", f"Bearer {self._token}"),
            ),
        )

    @rest.get("{self._event_url}")
    def get_issue(self) -> Issue:  # type: ignore[empty-body]
        pass

    @rest.get("{self._event_url}")
    def get_pull_request(self) -> PullRequest:  # type: ignore[empty-body]
        pass
