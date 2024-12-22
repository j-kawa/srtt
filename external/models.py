from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field, RootModel


T = TypeVar("T")


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
    platform: Optional[str] = Field(pattern=r"[IVX]*")
    line: int


class RawRoute(BaseModel):
    trainWeight: int
    trainLength: int
    locoType: Optional[str]
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


class RawRoutes(RootModel[list[RawRoute]]):
    root: list[RawRoute]


class RawResponse(BaseModel, Generic[T]):
    result: bool
    data: T
    count: int
    description: str


class RawServer(BaseModel):
    ServerCode: str = Field(pattern=r"[a-z\d]+")
    ServerName: str
    ServerRegion: str
    IsActive: bool
    id: str


class RawServers(RootModel[list[RawServer]]):
    root: list[RawServer]


RawServersResponse = RawResponse[RawServers]


class TrainData(BaseModel):
    VDDelayedTimetableIndex: int
    InBorderStationArea: bool


class RawTrain(BaseModel):
    TrainNoLocal: str
    Vehicles: list[str]
    TrainData: TrainData
    RunId: str
    id: str
    Type: Literal["user", "bot"]


class RawTrains(RootModel[list[RawTrain]]):
    root: list[RawTrain]


RawTrainsResponse = RawResponse[RawTrains]
