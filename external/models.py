from typing import Literal, Optional

from pydantic import BaseModel, Field, RootModel, TypeAdapter


class Meta(BaseModel):
    sync_ts: int


class RawRoutePoint(BaseModel):
    stationCategory: Optional[Literal["A", "B", "C", "D", "E"]]
    trainType: str = Field(pattern=r"[A-Z]{3}")
    nameOfPoint: str
    nameForPerson: str
    displayedTrainNumber: str = Field(pattern=r"\d+")
    mileage: float
    maxSpeed: int
    stopType: Literal["CommercialStop", "NoncommercialStop", "NoStopOver"]
    supervisedBy: Optional[str]
    radioChanels: str
    pointId: str = Field(pattern=r"\d+")
    track: Optional[int]
    arrivalTime: Optional[str] = Field(
        pattern=r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    )
    departureTime: Optional[str] = Field(
        pattern=r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    )
    platform: Optional[str] = Field(pattern=r"[IVX]+")
    line: int


class RawRoute(BaseModel):
    trainWeight: int
    trainLength: int
    locoType: str
    trainName: str
    startStation: str
    endStation: str
    trainNoInternational: Literal[""]
    trainNoLocal: str = Field(pattern=r"\d+")
    continuesAs: Literal[""]
    endsAt: str = Field(pattern=r"\d\d:\d\d:\d\d")
    startsAt: str = Field(pattern=r"\d\d:\d\d:\d\d")
    runId: str
    timetable: list[RawRoutePoint]


class RawRoutes(RootModel):
    root: list[RawRoute]


class RawServer(BaseModel):
    ServerCode: str = Field(pattern=r"[a-z\d]+")
    ServerName: str
    ServerRegion: str
    IsActive: bool
    id: str


class RawServers(RootModel):
    root: list[RawServer]


class RawServersResponse(BaseModel):
    result: bool
    data: RawServers
    count: int
    description: str


def load(path: str, type_: type):
    with open(path, "rb") as f:
        data = f.read()
    return TypeAdapter(type_).validate_json(data)
