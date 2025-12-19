from unittest.mock import patch

import bs4
import pytest
import sulguk

from notifier.application.services import RenderService


def test_format_body_empty_returns_input():
    service = RenderService(custom_labels=[], join_input_with_list=False)

    assert service.format_body("") == ""


def test_format_body_strips_blob_wrappers():
    service = RenderService(custom_labels=[], join_input_with_list=False)

    html = """
    <div>
        <div class="blob-wrapper"><p>code block</p></div>
        <p>real content</p>
    </div>
    """

    result = service.format_body(html)

    soup = bs4.BeautifulSoup(result, "lxml")
    # blob-wrapper content must be removed
    assert not soup.find_all(class_="blob-wrapper")
    assert "real content" in soup.text


def test_format_body_joins_input_lists(monkeypatch):
    service = RenderService(custom_labels=[], join_input_with_list=True)

    html = """
    <ul>
        <li><input type="checkbox"/> item 1</li>
        <li><input type="checkbox"/> item 2</li>
    </ul>
    """

    result = service.format_body(html)
    soup = bs4.BeautifulSoup(result, "lxml")

    # top-level ul should become div, li become div as well
    assert not soup.find("ul")
    divs = soup.find_all("div")
    assert any("item 1" in d.text for d in divs)
    assert any("item 2" in d.text for d in divs)


@patch("notifier.application.services.sulguk.transform_html")
def test_format_body_invalid_html_falls_back(mock_transform_html):
    service = RenderService(custom_labels=[], join_input_with_list=False)

    # Force sulguk.transform_html to raise and verify fallback
    mock_transform_html.side_effect = RuntimeError("boom")

    assert service.format_body("<p>broken</p>") == "<p></p>"


@pytest.mark.parametrize(
    ("labels", "custom", "expected"),
    [
        (["bug"], [], "#bug<br/>"),
        (["Bug Report"], [], "#bug_report<br/>"),
        (["high-priority"], [], "#high_priority<br/>"),
        (["Feature Request!!!"], [], "#feature_request<br/>"),
        (["Version 2.0"], [], "#version_20<br/>"),
        (["already_normalized"], [], "#already_normalized<br/>"),
        (["Test@#$%^&*()Label"], [], "#testlabel<br/>"),
        (["bug"], ["custom"], "#bug #custom<br/>"),
    ],
)
def test_format_labels(labels, custom, expected):
    service = RenderService(custom_labels=custom, join_input_with_list=False)

    assert service.format_labels(labels) == expected


