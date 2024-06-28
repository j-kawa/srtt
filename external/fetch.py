from typing import TypeVar
from urllib.parse import urlencode, urlunsplit

import requests
from pydantic import TypeAdapter

from .models import RawRoutes, RawServers, RawServersResponse


T = TypeVar('T')


def make_url(host: str, path: str, params: dict[str, str]) -> str:
    return urlunsplit(("https", host, path, urlencode(params), ""))


def get(url: str, type_: type[T]) -> T:
    print("GET ", url)
    resp = requests.get(url)
    resp.raise_for_status()
    ta = TypeAdapter(type_)
    return ta.validate_json(resp.content)


def load(path: str, type_: type[T]) -> T:
    with open(path, "rb") as f:
        data = f.read()
    ta = TypeAdapter(type_)
    return ta.validate_json(data)


def get_servers() -> RawServers:
    url = "https://panel.simrail.eu:8084/servers-open"
    resp = get(url, RawServersResponse)
    return resp.data


def get_routes(code: str) -> RawRoutes:
    url = make_url(
        "api1.aws.simrail.eu:8082",
        "/api/getAllTimetables",
        {"serverCode": code}
    )
    return get(url, RawRoutes)


def get_timezone(code: str) -> int:
    url = make_url(
        "api1.aws.simrail.eu:8082",
        "/api/getTimeZone",
        {"serverCode": code}
    )
    return get(url, int)
