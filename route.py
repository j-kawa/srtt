import dataclasses
from datetime import datetime, time
from enum import Enum
from itertools import count, groupby
import re
from typing import Optional

from external.models import RawRoute, RawRoutes
from point import PointDetails, StopType
from utils import parse_ts


NAME_REGEX = re.compile(r'(?P<kind>.+) - ".+"')


class RoutePointStatus(Enum):
    PLAYABLE = 1
    OTHER_PLAYABLE = 2  # playable in different part
    UNPLAYABLE = 3


@dataclasses.dataclass
class RoutePoint:
    point_id: str
    entry_time: Optional[datetime]
    exit_time: Optional[datetime]
    stop_type: StopType
    line: int
    platform: Optional[str]
    track: Optional[int]
    kind: str
    max_speed: int
    status: RoutePointStatus

    def get_entry_datetime(self) -> datetime:
        return self.entry_time or self.exit_time

    def get_exit_datetime(self) -> datetime:
        return self.exit_time or self.entry_time

    def get_entry_time(self) -> time:
        return (self.entry_time or self.exit_time).time()

    def get_exit_time(self) -> time:
        return (self.exit_time or self.entry_time).time()


@dataclasses.dataclass
class Route:

    # logical parameters
    train_no: str
    route_part: Optional[int]
    route_kind: str
    route_points: list[RoutePoint]

    # physical parameters
    train_type: Optional[str]
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

    def get_start_time(self) -> datetime:
        return self.start().get_entry_time()

    def get_scenario_points(self) -> list[RoutePoint]:
        return [
            point
            for point
            in self.route_points
            if point.status == RoutePointStatus.PLAYABLE
        ]

    def get_route_kind_short(self) -> str:
        if match_ := NAME_REGEX.fullmatch(self.route_kind):
            return match_.groupdict()["kind"]
        return self.route_kind

    def get_train_type(self) -> str:
        return self.train_type or "?"


def make_route(
        raw_route: RawRoute,
        part_ids: set[str],
        route_part: Optional[int],
        points: dict[str, PointDetails],
) -> Route:
    return Route(
        train_no=raw_route.trainNoLocal,
        route_part=route_part,
        route_kind=raw_route.trainName,
        train_type=raw_route.locoType,
        train_length=raw_route.trainLength,
        train_weight=raw_route.trainWeight,
        route_points=[RoutePoint(
            point_id=raw_point.pointId,
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
                if not points[raw_point.pointId].ingame
                else RoutePointStatus.PLAYABLE
                if raw_point.pointId in part_ids
                else RoutePointStatus.OTHER_PLAYABLE
            ),
        ) for raw_point in raw_route.timetable],
    )


def get_routes(
        routes: RawRoutes,
        points: dict[str, PointDetails]
) -> list[Route]:
    ret = []
    for raw_route in routes.root:
        parts = []
        parts_iter = groupby(
            (route.pointId for route in raw_route.timetable),
            key=lambda point_id: points[point_id].ingame
        )
        for ingame, point_ids in parts_iter:
            if not ingame:
                continue
            point_ids = set(point_ids)
            if len(point_ids) == 1:  # remove when testing things
                continue
            parts.append(point_ids)
        route_part_iter = count(1)
        route_part = None
        for part in parts:
            if len(parts) > 1:
                route_part = next(route_part_iter)
            ret.append(make_route(raw_route, part, route_part, points))
    return ret
