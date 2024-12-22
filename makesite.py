import dataclasses
import os
import shutil
from collections import Counter
from itertools import chain
from typing import Any, Hashable, Iterable, Optional

import jinja2
from more_itertools import minmax

from consts import MAIN_UNITS
from db import Database
from db.expr import All, Asc, Desc, Eq, Field, Gte, Value
from db.models import Train, deserialize_composition
from display import (
    Range,
    format_route_no,
    format_stop_type,
    format_timedelta,
    format_ts_iso_minutes,
    format_ts_rfc_7231,
)
from external.client import load_file
from external.models import Meta, RawRoutes, RawServers
from point import PointDetails, StopType, get_points
from prefix import get_prefixes
from resources import RESOURCES_VERSIONED, get_resource_path, get_resources
from route import Route, RoutePointStatus, get_routes
from utils import time_secs
from vehicles import parse_vehicle


env = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__),
    autoescape=jinja2.select_autoescape(),
    undefined=jinja2.StrictUndefined,
)


@dataclasses.dataclass
class RootCtx:
    sync_ts: str
    resources: dict[str, str]


@dataclasses.dataclass
class GenConfig:
    db: Database
    src: str
    dst: str


@dataclasses.dataclass(frozen=True)
class RouteDisc:
    train_type: str
    point_ids: tuple[int, ...]
    route_part: Optional[int]
    other: Hashable  # opaque identifier data

    @classmethod
    def from_route(cls, route: Route) -> "RouteDisc":
        points = route.get_scenario_points()
        return cls(
            train_type=route.get_train_type(),
            point_ids=tuple(point.point_id for point in points),
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


@dataclasses.dataclass
class Server:
    code: str
    name: str
    tz: int


@dataclasses.dataclass
class TrainSet:
    main_unit: str
    vehicle_counts: Counter[str]
    length: int
    weight: int
    first_seen: int
    last_seen: int


def get_trainsets(db: Database, code: str, since: int, only: set[str]):
    ret = {}
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
            first_seen=format_ts_iso_minutes(train.first_seen_server),
            last_seen=format_ts_iso_minutes(train.last_seen_server),
        ))
    return ret


@dataclasses.dataclass
class TrainSetStats:
    main_units: list[str]
    length: Range[int]
    weight: Range[int]
    accurate: bool


def get_trainset_stats(
        trainsets: dict[str, list[TrainSet]],
        routes: Iterable[Route],
) -> TrainSetStats:
    accurate = True
    main_units = set()
    lengths = weights = ()

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
        length=Range(*lengths),
        weight=Range(*weights),
        accurate=accurate,
    )


def gen(
        template: str,
        destdir: str,
        name: str,
        root_ctx: RootCtx,
        ctx: dict[str, Any],
):
    path = os.path.join(destdir, name)
    print("GEN ", path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    env.get_template(template).stream(ctx, g=root_ctx).dump(path)


def gen_tt_by_start(
        server: Server,
        destdir: str,
        name: str,
        points: dict[str, PointDetails],
        routes: list[Route],
        trainsets: dict[str, list[TrainSet]],
        root_ctx: RootCtx,
):
    data = []
    for route in sorted(routes, key=Route.get_start_time):
        trainset_stats = get_trainset_stats(trainsets, [route])
        data.append({
            "no": format_route_no(route),
            "train_type": route.get_train_type(),
            "train_name": route.train_name,
            "start_time": route.get_start_time().strftime("%H:%M"),
            "duration": format_timedelta(
                route.end().get_exit_datetime()
                - route.start().get_entry_datetime()
            ),
            "main_units": trainset_stats.main_units,
            "max_speed": max(
                (point.max_speed for point in route.get_scenario_points()),
                default=0
            ),
            "train_length": trainset_stats.length,
            "train_weight": trainset_stats.weight,
            "start_point": points[route.start().point_id].get_human_name(),
            "end_point": points[route.end().point_id].get_human_name(),
            "inaccurate": not trainset_stats.accurate,
            "compositions": {
                tuple(ts.vehicle_counts.items())
                for ts
                in trainsets.get(route.train_no, [])
            },
        })

    gen("start.html", destdir, name, root_ctx, {
        "data": data,
        "server": server,
    })


def gen_tt_by_route(
        server: Server,
        destdir: str,
        name: str,
        points: dict[str, PointDetails],
        routes: list[Route],
        trainsets: dict[str, list[TrainSet]],
        root_ctx: RootCtx,
) -> dict[str, tuple[str, str]]:
    all_numbers = {r.train_no for r in routes}

    groups = {}
    for route in routes:
        disc = RouteDisc.from_route(route)
        groups.setdefault(disc, []).append(route)

    prefixes = {}
    for disc, routes in groups.items():
        numbers = {r.train_no for r in routes}
        prefixes[disc] = tuple(sorted(
            get_prefixes(numbers, all_numbers - numbers)
        ))

    data = []
    for disc, prefixes in sorted(prefixes.items(), key=lambda pair: (
            len(pair[1][0]),
            pair[1]
    )):
        group = groups[disc]
        trainset_stats = get_trainset_stats(trainsets, group)
        data.append({
            "prefixes": prefixes,
            "part": str(disc.route_part or ""),
            "train_type": disc.train_type,
            "start": points[disc.point_ids[0]].get_human_name(),
            "end": points[disc.point_ids[-1]].get_human_name(),
            "duration": Range.from_minmax(iterable=(
                r.end().get_exit_datetime() - r.start().get_entry_datetime()
                for r
                in group
            ), fmt=format_timedelta),
            "main_units": trainset_stats.main_units,
            "max_speed": Range.from_minmax(
                max(p.max_speed for p in r.get_scenario_points())
                for r
                in group
            ),
            "train_length": trainset_stats.length,
            "train_weight": trainset_stats.weight,
            "inaccurate": not trainset_stats.accurate,
            "routes": [{
                "start_time": route.get_start_time(),
                "number": format_route_no(route),
            } for route in sorted(group, key=Route.get_start_time)]
        })

    gen("route.html", destdir, name, root_ctx, {
        "has_parts": any(disc.route_part for disc in groups),
        "data": data,
        "server": server,
    })

    return {
        route["number"]: (
            routes[(idx - 1) % len(routes)]["number"],
            routes[(idx + 1) % len(routes)]["number"],
        )
        for routes in (row["routes"] for row in data)
        for idx, route in enumerate(routes)
    }


def gen_train(
        server: Server,
        destdir: str,
        name: str,
        points: dict[str, PointDetails],
        route: Route,
        adj: tuple[str, str],
        trainsets: dict[str, list[TrainSet]],
        root_ctx: RootCtx,
):
    trainset_stats = get_trainset_stats(trainsets, [route])

    prev_no, next_no = adj
    params = {
        "train_number": route.train_no,
        "route_part": route.route_part or "",
        "train_name": route.train_name,
        "train_type": route.get_train_type(),
        "main_units": trainset_stats.main_units,
        "length": trainset_stats.length,
        "weight": trainset_stats.weight,
        "inaccurate": not trainset_stats.accurate,
        "prev": prev_no,
        "next": next_no,
    }
    path = [{
        "point_id": point.point_id,
        "name": points[point.point_id].name,
        "prefix": points[point.point_id].prefix,
        "entry_time": (
            point.get_entry_time().strftime("%H:%M")
            if point.get_entry_time() != point.get_exit_time()
            else "--:--"
        ),
        "exit_time": point.get_exit_time().strftime("%H:%M"),
        "line": point.line,
        "stop_type": format_stop_type(point.stop_type),
        "platform": point.platform or "",
        "track": point.track or "",
        "is_active": point.status == RoutePointStatus.PLAYABLE,
        "speed_limit": point.max_speed,
    } for point in route.route_points]

    gen("train.html", destdir, name, root_ctx, {
        "path": path,
        "params": params,
        "trainsets": trainsets.get(route.train_no, []),
        "server": server,
    })


def make_server(
        destdir: str,
        server: Server,
        routes: RawRoutes,
        trainsets: dict[str, list[TrainSet]],
        root_ctx: RootCtx,
) -> set[str]:
    files = set()
    points = get_points(routes)
    routes = get_routes(routes, points)

    name = f"{server.code}/tt-by-start.html"
    gen_tt_by_start(server, destdir, name, points, routes, trainsets, root_ctx)
    files.add(name)

    name = f"{server.code}/tt-by-route.html"
    adj = gen_tt_by_route(
        server,
        destdir,
        name,
        points,
        routes,
        trainsets,
        root_ctx
    )
    files.add(name)

    for route in routes:
        name = f"{server.code}/train/{format_route_no(route)}.html"
        gen_train(
            server,
            destdir,
            name,
            points,
            route,
            adj[format_route_no(route)],
            trainsets,
            root_ctx,
        )
        files.add(name)

    return files


def copy_resources(destdir: str, resources: dict[str, str]):
    for src_name, dst_name in resources.items():
        src = get_resource_path(src_name)
        dst = os.path.join(destdir, dst_name)
        print("COPY", dst)
        shutil.copy(src, dst)


def make_site(
        cfg: GenConfig,
        root_ctx: RootCtx,
        servers: list[Server],
) -> set[str]:
    files = set()

    copy_resources(cfg.dst, root_ctx.resources)
    files.update(root_ctx.resources.values())

    gen("index.html", cfg.dst, "index.html", root_ctx, {
        "servers": servers,
        "server": None,
    })
    files.add("index.html")

    gen("about.html", cfg.dst, "about.html", root_ctx, {"server": None})
    files.add("about.html")

    week_ago = time_secs() - (7 * 24 * 3600)
    for server in servers:
        path = os.path.join(cfg.src, "servers", f"{server.code}.json")
        tt = load_file(path, RawRoutes)
        train_numbers = {route.trainNoLocal for route in tt.root}
        trainsets = get_trainsets(cfg.db, server.code, week_ago, train_numbers)
        server_files = make_server(cfg.dst, server, tt, trainsets, root_ctx)
        files.update(server_files)

    return files


def cleanup_files(directory: str, keep: set[str]):
    for root, _, files in os.walk(directory):
        for file in files:
            name = os.path.relpath(os.path.join(root, file), directory)
            if name in keep:
                continue
            path = os.path.join(directory, name)
            print("DEL ", path)
            os.unlink(path)


def make(db: Database, src: str, dst: str, only_code: Optional[str]):
    cfg = GenConfig(db, src, dst)

    sync_ts = load_file(os.path.join(cfg.src, "meta.json"), Meta).sync_ts
    resources = get_resources(RESOURCES_VERSIONED)

    root_ctx = RootCtx(
        sync_ts=format_ts_rfc_7231(sync_ts),
        resources=resources,
    )

    servers = load_file(os.path.join(cfg.src, "servers.json"), RawServers)

    servers = [
        Server(
            code=server.ServerCode,
            name=server.ServerName,
            tz=load_file(os.path.join(
                cfg.src,
                "timezones",
                f"{server.ServerCode}.json"
            ), int)
        )
        for server
        in servers.root
        if only_code is None or server.ServerCode == only_code
    ]
    if not servers:
        raise ValueError("No servers")

    files = make_site(cfg, root_ctx, servers)

    cleanup_files(cfg.dst, keep=files)
