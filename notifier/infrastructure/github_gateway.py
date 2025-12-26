import os
from typing import Any

from adaptix import P, Retort, loader, name_mapping, Chain
from descanso import RestBuilder
from descanso import request_transformers as rt
from descanso.http.requests import RequestsClient
from requests import Session

from notifier.application import interfaces
from notifier.domain.entities import Issue, PullRequest

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
]


def body_pre_loader(data: dict[str, Any]) -> dict[str, Any]:
    if "body_html" not in data:
        data["body_html"] = ""
    return data


gh_recipe = [
    *issue_recipe,
    *pr_recipe,
    loader(P[Issue, PullRequest], body_pre_loader, Chain.FIRST),
    loader(P[Issue, PullRequest].labels, lambda labels: [label["name"] for label in labels])
]

rest = RestBuilder(
    request_body_dumper=Retort(),
    response_body_loader=Retort(recipe=gh_recipe),
    query_param_dumper=Retort(),
)

headers = (
    rt.Header("Accept", "application/vnd.github.v3.html+json"),
    rt.Header("X-GitHub-Api-Version", "2022-11-28"),
    rt.Header("Authorization", "Bearer {self._token}"),
)


def get_event_url() -> str:
    event_url = os.environ["EVENT_URL"]
    return event_url


class GithubGateway(RequestsClient, interfaces.Github):
    def __init__(
        self,
        token: str,
        base_url: str = "",
        session: Session | None = None
    ) -> None:
        self._token = token
        super().__init__(base_url, session or Session(), headers)

    @rest.get(get_event_url)
    def get_issue(self) -> Issue:  # type: ignore[empty-body]
        pass

    @rest.get(get_event_url)
    def get_pull_request(self) -> PullRequest:  # type: ignore[empty-body]
        pass
