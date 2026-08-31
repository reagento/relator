import sys
import time
from typing import Any

import requests


def send_webhook(*, payload: dict[str, Any], url: str, attempts: int) -> None:
    count = 0
    while count < attempts:
        response = requests.post(url, json=payload, timeout=30)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            print(response.content, file=sys.stderr)  # noqa: T201
            count += 1
            time.sleep(count * 2)
        else:
            print(  # noqa: T201
                f"Response: {response.status_code=} {response.text=}",
                file=sys.stdout,
            )
            return
