from notifier.domain.entities import Issue, PullRequest


def test_issue_repository_parsed_from_url():
    issue = Issue(
        id=1,
        title="Test",
        labels=[],
        url="https://github.com/owner/repo/issues/1",
        user="user",
        body="body",
    )

    assert issue.repository == "owner/repo"


def test_pull_request_dataclass_fields():
    pr = PullRequest(
        id=1,
        title="PR",
        labels=["bug"],
        url="https://github.com/owner/repo/pull/1",
        user="user",
        body="body",
        additions=10,
        deletions=2,
        head_ref="feature",
        base_ref="main",
        repository="owner/repo",
    )

    assert pr.repository == "owner/repo"
    assert pr.additions == 10
    assert pr.deletions == 2


