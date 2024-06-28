from datetime import datetime, timedelta
from typing import Callable, Generic, Iterable, TypeVar

from more_itertools import minmax

from point import StopType
from route import Route


T = TypeVar("T")


class Range(Generic[T]):
    SEP = "-"

    def __init__(self, low: T, high: T, fmt: Callable[[T], str] = str):
        self.low = low
        self.high = high
        self.fmt = fmt

    def __str__(self):
        if self.low == self.high:
            return self.fmt(self.low)
        return f"{self.fmt(self.low)}{self.SEP}{self.fmt(self.high)}"

    @classmethod
    def from_minmax(cls, iterable: Iterable[T], fmt: Callable[[T], str] = str):
        return cls(*minmax(iterable), fmt)


def format_timedelta(td: timedelta) -> str:
    secs = td.days * 24 * 3600 + td.seconds
    return f"{secs // 3600}:{secs // 60 % 60:02}"


def format_route_no(route: Route) -> str:
    if route.route_part is None:
        return route.train_no
    return f"{route.train_no}-{route.route_part}"


def format_stop_type(st: StopType) -> str:
    return {
        StopType.BZ: "",
        StopType.PT: "pt",
        StopType.PH: "ph",
    }[st]


def format_ts(ts: int) -> str:
    return datetime.utcfromtimestamp(ts).strftime("%a, %d %b %Y %H:%M:%S GMT")
