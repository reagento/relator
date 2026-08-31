import dataclasses
import re
import sys

import bs4
import sulguk


@dataclasses.dataclass(frozen=True, kw_only=True)
class RenderService:
    custom_labels: list[str]
    join_input_with_list: bool

    def format_body(self, body: str) -> str:
        if not body:
            return body

        soup = bs4.BeautifulSoup(body, "lxml")

        for s in soup.find_all(class_="blob-wrapper"):
            s.extract()

        if self.join_input_with_list:
            for ul in soup.find_all("ul"):
                if ul.find("input"):
                    ul.name = "div"
                    for li in ul.find_all("li"):
                        li.name = "div"

        result = str(soup)

        try:
            sulguk.transform_html(result, base_url="https://github.com")
        except Exception as e:  # noqa: BLE001
            print(f"Error transforming HTML: {e}", file=sys.stderr)  # noqa: T201
            return "<p></p>"
        else:
            return result

    def format_labels(self, labels: list[str]):
        return (
            " ".join(
                f"#{self._parse_label(label)}"
                for label in labels + self.custom_labels
                if self._parse_label(label)
            )
            + "<br/>"
        )

    def _parse_label(self, raw_label: str) -> str:
        """
        Bug Report -> bug_report
        high-priority -> high_priority
        Feature Request!!! -> feature_request
        Version 2.0 -> version_20
        Critical Bug - Urgent!!! -> critical_bug___urgent
        Багрепорт - ...
        already_normalized -> already_normalized
        Test@#$%^&*()Label -> testlabel
        ... -> ...
        """
        parsed_label = raw_label.lower().replace(" ", "_").replace("-", "_")
        return re.sub(r"[^a-zA-Z0-9_]", "", parsed_label)
