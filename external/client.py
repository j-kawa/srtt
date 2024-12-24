import time
from types import TracebackType
from typing import AnyStr, Optional, Type, TypeVar
from urllib.parse import urlencode, urlunsplit

from pydantic import TypeAdapter
from requests import Session

from utils import time_millis

from .models import (
    RawRoutes,
    RawServers,
    RawServersResponse,
    RawTrains,
    RawTrainsResponse,
)


T = TypeVar('T')


def validate_json(data: AnyStr, type_: type[T]) -> T:
    ta = TypeAdapter(type_)
    return ta.validate_json(data)


def make_url(host: str, path: str, params: dict[str, str]) -> str:
    return urlunsplit(("https", host, path, urlencode(params), ""))


def load_file(path: str, type_: type[T]) -> T:
    with open(path, "rb") as f:
        return validate_json(f.read(), type_)


class ApiClient:

    def __init__(self, interval: float, user_agent: Optional[str] = None):
        self.session = Session()
        self.next_request_time_ms = 0
        self.interval_ms = int(interval * 1_000)
        self.timeout = 15

        self.headers = {}
        if user_agent is not None:
            self.headers["User-Agent"] = user_agent

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    def _sleep_ratelimit(self) -> None:
        now = time_millis()
        sleep_duration = self.next_request_time_ms - now
        if sleep_duration > 0:
            time.sleep(sleep_duration / 1_000)
        self.next_request_time_ms = (
            max(now, self.next_request_time_ms)
            + self.interval_ms
        )

    def get(self, url: str, type_: type[T]) -> T:
        self._sleep_ratelimit()
        print("GET ", url)
        resp = self.session.get(
            url,
            timeout=self.timeout,
            headers=self.headers,
        )
        resp.raise_for_status()
        return validate_json(resp.content, type_)

    def get_servers(self) -> RawServers:
        url = "https://panel.simrail.eu:8084/servers-open"
        return self.get(url, RawServersResponse).data

    def get_routes(self, code: str) -> RawRoutes:
        url = make_url(
            "api1.aws.simrail.eu:8082",
            "/api/getAllTimetables",
            {"serverCode": code},
        )
        return self.get(url, RawRoutes)

    def get_time(self, code: str) -> int:
        url = make_url(
            "api1.aws.simrail.eu:8082",
            "/api/getTime",
            {"serverCode": code},
        )
        return self.get(url, int)

    def get_trains(self, code: str) -> RawTrains:
        url = make_url(
            "panel.simrail.eu:8084",
            "/trains-open",
            {"serverCode": code},
        )
        return self.get(url, RawTrainsResponse).data
