import dataclasses
import os
import shutil
import typing as t
from collections import Counter
from datetime import datetime, time, timedelta, timezone
from itertools import chain

import jinja2
from more_itertools import minmax

from consts import CONTROLLABLE_POINTS, MAIN_UNITS
from db import Database
from db.expr import All, Asc, Desc, Eq, Field, Gte, Value
from db.models import Train, deserialize_composition
from external.client import load_file
from external.models import Meta, RawRoutes, RawServers
from prefix import get_prefixes
from resources import get_resource_path, get_resources
from route import Route, RoutePointStatus, StopType, get_routes
from utils import SupportsLt, pick_codes, time_secs
from vehicles import parse_vehicle


if t.TYPE_CHECKING:
    from _typeshed import DataclassInstance


env = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__),
    autoescape=jinja2.select_autoescape(),
    undefined=jinja2.StrictUndefined,
    lstrip_blocks=True,
    trim_blocks=True,
    line_statement_prefix='#',
    keep_trailing_newline=True,
)


F = t.TypeVar("F", bound=t.Callable[..., t.Any])


def register_filter(env: jinja2.Environment) -> t.Callable[[F], F]:
    def inner(func: F) -> F:
        env.filters[func.__name__] = func
        return func
    return inner


@register_filter(env)
def td_minutes(td: timedelta) -> str:
    secs = td.days * 24 * 3600 + td.seconds
    return f"{secs // 3600}:{secs // 60 % 60:02}"


@register_filter(env)
def range(rng: "Range[timedelta]") -> str:
    if rng.low == rng.high:
        return str(rng.low)
    return f"{rng.low}-{rng.high}"


@register_filter(env)
def td_range_minutes(rng: "Range[timedelta]") -> str:
    if rng.low == rng.high:
        return td_minutes(rng.low)
    return f"{td_minutes(rng.low)}-{td_minutes(rng.high)}"


@register_filter(env)
def to_utc(dt: datetime) -> datetime:
    return dt.astimezone(timezone.utc)


TCtx = t.TypeVar("TCtx", bound="DataclassInstance")


@dataclasses.dataclass(slots=True)
class BaseCtx:
    resources: dict[str, str]
    time_offset: t.Optional[timedelta]
    last_sync: datetime

    def get_time_offset_ms(self) -> t.Optional[int]:
        if self.time_offset is None:
            return None
        return self.time_offset // timedelta(milliseconds=1)


class Template(t.Generic[TCtx]):
    TEMPLATE_PATH: str

    def __init__(self, base_ctx: BaseCtx, ctx: TCtx):
        self.base_ctx = base_ctx
        self.ctx = ctx

    def get_output_path(self) -> str:
        raise NotImplementedError


class Renderer:
    def __init__(self, destdir: str):
        self.existing_paths = set[str]()
        self.destdir = destdir

    def _ensure_dir_exists(self, directory: str) -> None:
        if directory in self.existing_paths:
            return
        os.makedirs(directory, exist_ok=True)
        self.existing_paths.add(directory)

    def render(self, tpl: "Template[DataclassInstance]") -> str:
        path = tpl.get_output_path()

        dest_path = os.path.join(self.destdir, path)
        self._ensure_dir_exists(os.path.dirname(dest_path))

        print("GEN ", path)
        env.get_template(tpl.TEMPLATE_PATH).stream(
            base_ctx=tpl.base_ctx,
            ctx=tpl.ctx,
        ).dump(dest_path)
        return path


@dataclasses.dataclass(slots=True)
class GenConfig:
    db: Database
    src: str


@dataclasses.dataclass(slots=True, frozen=True)
class RouteDisc:
    train_type: str
    point_names: tuple[str, ...]
    route_start: str
    route_end: str
    route_part: t.Optional[int]
    other: t.Hashable  # opaque identifier data

    @classmethod
    def from_route(cls, route: Route) -> t.Self:
        points = route.get_scenario_points()
        return cls(
            train_type=route.get_train_type(),
            point_names=tuple(point.name for point in points),
            route_start=points[0].get_nice_name(),
            route_end=points[-1].get_nice_name(),
            route_part=route.route_part,
            other=(
                len(route.train_no),
                tuple((
                    # disable, for now (probably forever)
                    # point.kind,
                    # point.line,
                    point.stop_type == StopType.PH,
                ) for point in points),
            )
        )


@dataclasses.dataclass(slots=True)
class Server:
    code: str
    time_offset: timedelta


@dataclasses.dataclass(slots=True)
class TrainSet:
    main_unit: str
    vehicle_counts: Counter[str]
    length: int
    weight: int

    # server time
    first_seen: datetime
    last_seen: datetime


def get_trainsets(
        db: Database,
        code: str,
        since: int,
        only: set[str]
) -> dict[str, list[TrainSet]]:
    ret = dict[str, list[TrainSet]]()
    with db.transaction() as tx:
        ids_trains = tx.select(
            model=Train,
            where=All(
                Eq(Field("server"), Value(code)),
                Gte(Field("last_seen"), Value(since)),
            ),
            order=[Asc("train_number"), Desc("last_seen")],
        )
    for _, train in ids_trains:
        if train.train_number not in only:
            continue
        vehicles = [
            parse_vehicle(ident)
            for ident
            in deserialize_composition(train.composition)
        ]
        ret.setdefault(train.train_number, []).append(TrainSet(
            main_unit=vehicles[0].name,
            vehicle_counts=Counter(v.name for v in vehicles),
            length=round(sum(vehicle.length for vehicle in vehicles)),
            weight=round(sum(vehicle.weight for vehicle in vehicles)),
            first_seen=datetime.utcfromtimestamp(train.first_seen_server),
            last_seen=datetime.utcfromtimestamp(train.last_seen_server),
        ))
    return ret


TLess = t.TypeVar("TLess", bound=SupportsLt)


class Range(t.Generic[TLess]):
    SEP = "-"

    def __init__(self, low: TLess, high: TLess):
        self.low = low
        self.high = high
        self.fmt = str

    def __str__(self) -> str:
        raise ValueError()
        if self.low == self.high:
            return self.fmt(self.low)
        return f"{self.fmt(self.low)}{self.SEP}{self.fmt(self.high)}"

    @classmethod
    def from_minmax(
            cls,
            iterable: t.Iterable[TLess],
            fmt: t.Callable[[TLess], str] = str
    ) -> t.Self:
        return cls(*minmax(iterable))


@dataclasses.dataclass(slots=True)
class TrainSetStats:
    main_units: list[str]
    length: Range[int]
    weight: Range[int]
    accurate: bool


def get_trainset_stats(
        trainsets: dict[str, list[TrainSet]],
        routes: t.Iterable[Route],
) -> TrainSetStats:
    accurate = True
    main_units = set()
    lengths: tuple[int, ...] = ()
    weights: tuple[int, ...] = ()

    for route in routes:
        route_trainsets = trainsets.get(route.train_no, [])
        if not route_trainsets:
            main_units.add(MAIN_UNITS[route.main_unit or "?"])
            lengths = minmax([route.train_length, *lengths])
            weights = minmax([route.train_weight, *weights])
            accurate = False
            continue
        main_units.update(ts.main_unit for ts in route_trainsets)
        lengths = minmax(chain(
            (ts.length for ts in route_trainsets),
            lengths,
        ))
        weights = minmax(chain(
            (ts.weight for ts in route_trainsets),
            weights,
        ))

    return TrainSetStats(
        main_units=sorted(main_units),
        length=Range(lengths[0], lengths[1]),
        weight=Range(weights[0], weights[1]),
        accurate=accurate,
    )


def format_route_no(no: str, part: t.Optional[int]) -> str:
    if part is None:
        return no
    return f"{no}-{part}"


@dataclasses.dataclass(slots=True)
class IndexCtx:
    servers: list[Server]


@dataclasses.dataclass(slots=True)
class TrainStart:
    no: str
    type: str
    name: str
    start_time: time
    duration: timedelta
    main_units: list[str]
    max_speed: int
    length: Range[int]
    weight: Range[int]
    start_point: str
    end_point: str
    compositions: set[tuple[tuple[str, int], ...]]
    inaccurate: bool


@dataclasses.dataclass(slots=True)
class StartCtx:
    server: Server
    trains: list[TrainStart]


@dataclasses.dataclass(slots=True)
class RouteVariant:
    start_time: time
    no: str


@dataclasses.dataclass(slots=True)
class TrainRoute:
    prefixes: list[str]
    part: t.Optional[int]
    type: str
    start: str
    end: str
    duration: Range[timedelta]
    main_units: list[str]
    max_speed: Range[int]
    length: Range[int]
    weight: Range[int]
    variants: list[RouteVariant]
    inaccurate: bool


@dataclasses.dataclass(slots=True)
class RouteCtx:
    server: Server
    routes: list[TrainRoute]

    def has_parts(self) -> bool:
        return any(route.part is not None for route in self.routes)


@dataclasses.dataclass(slots=True)
class TrainPoint:
    point_id: str
    name: str
    prefix: t.Optional[str]
    entry_time: t.Optional[time]
    exit_time: time
    line: int
    stop_type: StopType
    platform: t.Optional[str]
    track: t.Optional[int]
    is_active: bool
    speed_limit: int


@dataclasses.dataclass(slots=True)
class TrainCtx:
    server: Server
    no: str
    part: t.Optional[int]
    name: str
    type: str
    main_units: list[str]
    length: Range[int]
    weight: Range[int]
    prev: str
    next: str
    inaccurate: bool
    trainsets: list[TrainSet]
    path: list[TrainPoint]


@dataclasses.dataclass(slots=True)
class EmptyCtx:
    pass


class IndexTemplate(Template[IndexCtx]):
    TEMPLATE_PATH = "index.html"

    def get_output_path(self) -> str:
        return "index.html"


class AboutTemplate(Template[EmptyCtx]):
    TEMPLATE_PATH = "about.html"

    def get_output_path(self) -> str:
        return "about.html"


class StartTemplate(Template[StartCtx]):
    TEMPLATE_PATH = "start.html"

    def get_output_path(self) -> str:
        return f"{self.ctx.server.code}/tt-by-start.html"


class RouteTemplate(Template[RouteCtx]):
    TEMPLATE_PATH = "route.html"

    def get_output_path(self) -> str:
        return f"{self.ctx.server.code}/tt-by-route.html"


class TrainTemplate(Template[TrainCtx]):
    TEMPLATE_PATH = "train.html"

    def get_output_path(self) -> str:
        no = format_route_no(self.ctx.no, self.ctx.part)
        return f"{self.ctx.server.code}/train/{no}.html"


def make_start_ctx(
        server: Server,
        routes: list[Route],
        trainsets: dict[str, list[TrainSet]],
) -> StartCtx:
    trains: list[TrainStart] = []
    for route in sorted(routes, key=Route.get_start_time):
        trainset_stats = get_trainset_stats(trainsets, [route])
        trains.append(TrainStart(
            no=format_route_no(route.train_no, route.route_part),
            type=route.get_train_type(),
            name=route.train_name,
            start_time=route.get_start_time(),
            duration=(
                route.end().get_exit_datetime()
                - route.start().get_entry_datetime()
            ),
            main_units=trainset_stats.main_units,
            max_speed=max(
                (point.max_speed for point in route.get_scenario_points()),
                default=0,
            ),
            length=trainset_stats.length,
            weight=trainset_stats.weight,
            start_point=route.start().get_nice_name(),
            end_point=route.end().get_nice_name(),
            compositions={
                tuple(ts.vehicle_counts.items())
                for ts
                in trainsets.get(route.train_no, [])
            },
            inaccurate=not trainset_stats.accurate,
        ))
    return StartCtx(server, trains)


def prefix_sort_key(disc_prefixes: tuple[RouteDisc, list[str]]) -> SupportsLt:
    _, prefixes = disc_prefixes
    return len(prefixes[0]), prefixes


def make_route_ctx(
        server: Server,
        routes: list[Route],
        trainsets: dict[str, list[TrainSet]],
) -> RouteCtx:
    all_numbers = {r.train_no for r in routes}

    groups = dict[RouteDisc, list[Route]]()
    for route in routes:
        disc = RouteDisc.from_route(route)
        groups.setdefault(disc, []).append(route)

    group_prefixes = dict[RouteDisc, list[str]]()
    for disc, routes in groups.items():
        numbers = {r.train_no for r in routes}
        group_prefixes[disc] = sorted(
            get_prefixes(numbers, all_numbers - numbers)
        )

    routes_ctx = list[TrainRoute]()
    for disc, prefixes in sorted(group_prefixes.items(), key=prefix_sort_key):
        group = groups[disc]
        trainset_stats = get_trainset_stats(trainsets, group)
        routes_ctx.append(TrainRoute(
            prefixes=prefixes,
            part=disc.route_part,
            type=disc.train_type,
            start=disc.route_start,
            end=disc.route_end,
            duration=Range.from_minmax(
                r.end().get_exit_datetime() - r.start().get_entry_datetime()
                for r
                in group
            ),
            main_units=trainset_stats.main_units,
            max_speed=Range.from_minmax(
                max(p.max_speed for p in r.get_scenario_points())
                for r
                in group
            ),
            length=trainset_stats.length,
            weight=trainset_stats.weight,
            variants=[RouteVariant(
                start_time=route.get_start_time(),
                no=format_route_no(route.train_no, route.route_part),
            ) for route in sorted(group, key=Route.get_start_time)],
            inaccurate=not trainset_stats.accurate,
        ))
    return RouteCtx(server, routes_ctx)


def make_train_ctx(
        server: Server,
        route: Route,
        prev: str,
        next_: str,
        trainsets: dict[str, list[TrainSet]],
) -> TrainCtx:
    trainset_stats = get_trainset_stats(trainsets, [route])
    path = [TrainPoint(
        point_id=point.point_id,
        name=point.name,
        prefix=CONTROLLABLE_POINTS.get(point.name),
        entry_time=(
            point.get_entry_time()
            if point.get_entry_time() != point.get_exit_time()
            else None
        ),
        exit_time=point.get_exit_time(),
        line=point.line,
        stop_type=point.stop_type,
        platform=point.platform,
        track=point.track,
        is_active=point.status == RoutePointStatus.PLAYABLE,
        speed_limit=point.max_speed,
    ) for point in route.route_points]

    return TrainCtx(
        server=server,
        no=route.train_no,
        part=route.route_part,
        name=route.train_name,
        type=route.get_train_type(),
        main_units=trainset_stats.main_units,
        length=trainset_stats.length,
        weight=trainset_stats.weight,
        inaccurate=not trainset_stats.accurate,
        prev=prev,
        next=next_,
        trainsets=trainsets.get(route.train_no, []),
        path=path,
    )


def iter_train_templates(
        server: Server,
        routes: list[Route],
        adj: dict[str, tuple[str, str]],
        trainsets: dict[str, list[TrainSet]],
        base_ctx: BaseCtx,
) -> t.Iterable[TrainTemplate]:
    for route in routes:
        prev, next_ = adj[format_route_no(route.train_no, route.route_part)]
        yield TrainTemplate(base_ctx, make_train_ctx(
            server, route, prev, next_, trainsets
        ))


def iter_server_templates(
        cfg: GenConfig,
        server: Server,
        resources: dict[str, str],
        last_sync: datetime,
        since: int,
) -> t.Iterable[Template[t.Any]]:
    base_ctx = BaseCtx(resources, server.time_offset, last_sync)
    tt_path = os.path.join(cfg.src, "servers", f"{server.code}.json")
    tt = load_file(tt_path, RawRoutes)
    train_numbers = {route.trainNoLocal for route in tt.root}

    trainsets = get_trainsets(cfg.db, server.code, since, train_numbers)
    routes = get_routes(tt)

    route_ctx = make_route_ctx(server, routes, trainsets)
    adj = {
        variant.no: (
            route.variants[(idx - 1) % len(route.variants)].no,
            route.variants[(idx + 1) % len(route.variants)].no,
        )
        for route in route_ctx.routes
        for idx, variant in enumerate(route.variants)
    }

    yield StartTemplate(base_ctx, make_start_ctx(
        server, routes, trainsets,
    ))
    yield RouteTemplate(base_ctx, route_ctx)
    yield from iter_train_templates(
        server, routes, adj, trainsets, base_ctx
    )


def iter_templates(
        cfg: GenConfig,
        servers: list[Server],
        resources: dict[str, str],
        last_sync: datetime
) -> t.Iterable[Template[t.Any]]:
    week_ago = time_secs() - (7 * 24 * 3600)
    base_ctx = BaseCtx(resources, None, last_sync)

    yield IndexTemplate(base_ctx, IndexCtx(servers))
    yield AboutTemplate(base_ctx, EmptyCtx())
    for server in servers:
        yield from iter_server_templates(
            cfg, server, resources, last_sync, week_ago
        )


def copy_resources(destdir: str, resources: dict[str, str]) -> t.Iterable[str]:
    for src_name, dst_name in resources.items():
        src = get_resource_path(src_name)
        dst = os.path.join(destdir, dst_name)
        print("COPY", dst_name)
        shutil.copy(src, dst)
    return resources.values()


def walk_files(directory: str) -> t.Iterable[str]:
    for root, _, files in os.walk(directory):
        for file in files:
            yield os.path.relpath(os.path.join(root, file), directory)


def cleanup_files(directory: str, keep: set[str]) -> None:
    for file in walk_files(directory):
        if file in keep:
            continue
        print("DEL ", file)
        os.unlink(os.path.join(directory, file))


def load_server_time_offset(src: str, code: str) -> timedelta:
    millis = load_file(os.path.join(src, "time_offsets", f"{code}.json"), int)
    return timedelta(milliseconds=millis)


def make(db: Database, src: str, dst: str, only_code: t.Optional[str]) -> None:
    cfg = GenConfig(db, src)

    sync_ts = load_file(os.path.join(cfg.src, "meta.json"), Meta).sync_ts
    last_sync = datetime.fromtimestamp(sync_ts)
    resources = get_resources()

    raw_servers = load_file(os.path.join(cfg.src, "servers.json"), RawServers)

    servers = [
        Server(code, load_server_time_offset(src, code))
        for code
        in pick_codes(
            only_code,
            (server.ServerCode for server in raw_servers.root)
        )
    ]

    renderer = Renderer(dst)
    files = {
        renderer.render(template)
        for template
        in iter_templates(cfg, servers, resources, last_sync)
    }
    files.update(copy_resources(dst, resources))

    cleanup_files(dst, files)
