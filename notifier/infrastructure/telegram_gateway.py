from dataclasses import dataclass
from typing import Any

from adaptix import Retort
from requests import Session
from requests.adapters import HTTPAdapter
from descanso import RestBuilder
from descanso.http.requests import RequestsClient
import sulguk

from notifier.application import interfaces

rest = RestBuilder(
    request_body_dumper=Retort(),
    response_body_loader=Retort(),
    query_param_dumper=Retort(),
)


@dataclass
class TgPayload:
    text: str
    entities: list[sulguk.data.MessageEntity]
    disable_web_page_preview: bool
    chat_id: str
    message_thread_id: str | None


class TelegramGateway(RequestsClient, interfaces.Telegram):

    def __init__(
        self,
        token: str,
        attemp_count: int,
        base_url: str = "https://api.telegram.org",
        session: Session | None = None,
    ) -> None:
        self._token = token
        tg_session = session or Session()
        tg_session.mount("https", HTTPAdapter(max_retries=attemp_count))
        super().__init__(base_url, tg_session)

    @rest.post("/bot{self._token}/sendMessage")
    def send_message(self, body: interfaces.TgPayload) -> Any:  # type: ignore[empty-body]
        pass
