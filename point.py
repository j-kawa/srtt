import dataclasses
from enum import IntEnum
from itertools import chain
from typing import Optional, Self, TypeVar

from consts import CONTROLLABLE_POINTS, INGAME_POINTS
from external.models import RawRoutePoint, RawRoutes


T = TypeVar("T")


class StopType(IntEnum):
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

    def display(self) -> Optional[str]:
        return {self.BZ: None, self.PH: "ph", self.PT: "pt"}[self]


def merge_optional(v1: T, v2: T) -> T:
    if v1 is None:
        return v2
    if v2 is None:
        return v1
    if v1 != v2:
        raise ValueError(f"cannot merge: {v1} != {v2}")
    return v1


@dataclasses.dataclass(slots=True)
class PointDetails:
    name: str
    supervisor: Optional[str]
    stop_types: set[StopType]
    ingame: bool
    prefix: Optional[str]
    station_category: Optional[str]

    @classmethod
    def from_raw(cls, raw: RawRoutePoint) -> Self:
        if raw.nameOfPoint != raw.nameForPerson:
            raise ValueError(
                f"point names differ: `{raw.nameOfPoint}`"
                f"!= `{raw.nameForPerson}`"
            )
        return cls(
            name=raw.nameOfPoint,
            supervisor=raw.supervisedBy,
            stop_types={StopType.from_string(raw.stopType)},
            ingame=raw.nameOfPoint in INGAME_POINTS,
            prefix=CONTROLLABLE_POINTS.get(raw.nameOfPoint),
            station_category=raw.stationCategory,
        )

    def merge(self, other: "PointDetails") -> None:
        assert self.name == other.name
        self.supervisor = merge_optional(self.supervisor, other.supervisor)
        self.station_category = merge_optional(
            self.station_category,
            other.station_category
        )
        self.stop_types.update(other.stop_types)

    def get_human_name(self) -> str:
        return self.supervisor or self.name


def get_points(routes: RawRoutes) -> dict[str, PointDetails]:
    ret = {}
    points = chain.from_iterable(route.timetable for route in routes.root)
    for point in points:
        id_ = point.pointId
        if id_ not in ret:
            ret[id_] = PointDetails.from_raw(point)
        else:
            ret[id_].merge(PointDetails.from_raw(point))
    return ret
