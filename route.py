import dataclasses
import enum
import typing as t
from datetime import datetime, time
from itertools import count, groupby, repeat

from more_itertools import ilen

from consts import INGAME_POINTS
from external.models import RawRoute, RawRoutePoint, RawRoutes
from utils import parse_ts


class StopType(enum.IntEnum):
    BZ = 0
    PH = 1
    PT = 2

    @classmethod
    def from_string(cls, stop_type: str) -> "StopType":
        return {
            "NoStopOver": cls.BZ,
            "CommercialStop": cls.PH,
            "NoncommercialStop": cls.PT,
        }[stop_type]

    def display(self) -> t.Optional[str]:
        return {self.BZ: None, self.PH: "ph", self.PT: "pt"}[self]


class RoutePointStatus(enum.IntEnum):
    PLAYABLE = 1
    OTHER_PLAYABLE = 2  # playable in different part
    UNPLAYABLE = 3


@dataclasses.dataclass(slots=True)
class RoutePoint:
    point_id: str
    name: str
    supervised_by: t.Optional[str]
    entry_time: t.Optional[datetime]
    exit_time: t.Optional[datetime]
    stop_type: StopType
    line: int
    platform: t.Optional[str]
    track: t.Optional[int]
    kind: str
    max_speed: int
    status: RoutePointStatus

    def get_entry_datetime(self) -> datetime:
        ret = self.entry_time or self.exit_time
        if ret is None:
            raise ValueError("no time specified")
        return ret

    def get_exit_datetime(self) -> datetime:
        ret = self.exit_time or self.entry_time
        if ret is None:
            raise ValueError("no time specified")
        return ret

    def get_entry_time(self) -> time:
        return self.get_entry_datetime().time()

    def get_exit_time(self) -> time:
        return self.get_exit_datetime().time()

    def get_nice_name(self) -> str:
        return self.supervised_by or self.name


@dataclasses.dataclass(slots=True)
class Route:

    # logical parameters
    train_no: str
    route_part: t.Optional[int]
    train_name: str
    route_points: list[RoutePoint]

    # physical parameters
    main_unit: t.Optional[str]
    train_length: int
    train_weight: int

    def start(self) -> RoutePoint:
        return next(
            p
            for p
            in self.route_points
            if p.status == RoutePointStatus.PLAYABLE
        )

    def end(self) -> RoutePoint:
        return next(
            p
            for p
            in reversed(self.route_points)
            if p.status == RoutePointStatus.PLAYABLE
        )

    def get_start_time(self) -> time:
        return self.start().get_entry_time()

    def get_scenario_points(self) -> list[RoutePoint]:
        return [
            point
            for point
            in self.route_points
            if point.status == RoutePointStatus.PLAYABLE
        ]

    def get_train_type(self) -> str:
        return ", ".join(sorted({
            p.kind
            for p
            in self.route_points
            if p.status == RoutePointStatus.PLAYABLE
        }))


def is_point_ingame(point: RawRoutePoint) -> bool:
    return point.nameOfPoint in INGAME_POINTS


def make_route_points(
        raw_points: list[RawRoutePoint],
        route_pattern: list[t.Optional[int]],
        route_part: t.Optional[int],
) -> list[RoutePoint]:
    return [
        RoutePoint(
            point_id=raw_point.pointId,
            name=raw_point.nameOfPoint,
            supervised_by=(raw_point.supervisedBy or "").strip() or None,
            entry_time=parse_ts(raw_point.arrivalTime),
            exit_time=parse_ts(raw_point.departureTime),
            stop_type=StopType.from_string(raw_point.stopType),
            line=raw_point.line,
            platform=raw_point.platform,
            track=raw_point.track,
            kind=raw_point.trainType,
            max_speed=raw_point.maxSpeed,
            status=(
                RoutePointStatus.UNPLAYABLE
                if not is_point_ingame(raw_point)
                else RoutePointStatus.PLAYABLE
                if route_part in [part_idx, None]
                else RoutePointStatus.OTHER_PLAYABLE
            ),
        )
        for raw_point, part_idx
        in zip(raw_points, route_pattern, strict=True)
    ]


def make_route(
        raw_route: RawRoute,
        route_pattern: list[t.Optional[int]],
        route_part: t.Optional[int],
) -> Route:
    return Route(
        train_no=raw_route.trainNoLocal,
        route_part=route_part,
        train_name=raw_route.trainName,
        main_unit=raw_route.locoType,
        train_length=raw_route.trainLength,
        train_weight=raw_route.trainWeight,
        route_points=make_route_points(
            raw_points=raw_route.timetable,
            route_pattern=route_pattern,
            route_part=route_part,
        ),
    )


def get_route_pattern(
        points: list[RawRoutePoint],
        min_size: int,
) -> tuple[int, list[t.Optional[int]]]:
    parts_iter = count(1)
    pattern: list[t.Optional[int]] = []
    for ingame, points_iter in groupby(points, is_point_ingame):
        size = ilen(points_iter)
        if ingame and size >= min_size:
            part = next(parts_iter)
        else:
            part = None
        pattern.extend(repeat(part, size))

    assert len(pattern) == len(points)
    return next(parts_iter) - 1, pattern


def get_route_parts(raw_route: RawRoute) -> list[Route]:
    num_parts, pattern = get_route_pattern(raw_route.timetable, 2)
    if num_parts == 1:
        return [make_route(raw_route, pattern, None)]
    return [
        make_route(raw_route, pattern, part)
        for part
        in range(1, num_parts + 1)
    ]


def get_routes(routes: RawRoutes) -> list[Route]:
    ret = []
    for raw_route in routes.root:
        ret.extend(get_route_parts(raw_route))
    return ret
