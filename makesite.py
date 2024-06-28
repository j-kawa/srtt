import dataclasses
import os
import shutil
from typing import Any, Hashable, Optional

import jinja2

from consts import TRAIN_TYPES
from display import (
    Range,
    format_route_no,
    format_stop_type,
    format_timedelta,
    format_ts,
)
from external.fetch import load
from external.models import Meta, RawRoutes, RawServers
from point import PointDetails, StopType, get_points
from prefix import get_prefixes
from resources import RESOURCES_VERSIONED, get_resource_path, get_resources
from route import Route, RoutePointStatus, get_routes


env = jinja2.Environment(
    loader=jinja2.PackageLoader(__name__),
    autoescape=jinja2.select_autoescape(),
    undefined=jinja2.StrictUndefined,
)


@dataclasses.dataclass(frozen=True)
class RootCtx:
    sync_ts: str
    resources: dict[str, str]


@dataclasses.dataclass(frozen=True)
class GenConfig:
    src: str
    dst: str


@dataclasses.dataclass(frozen=True)
class RouteDisc:
    train_name: str
    point_ids: tuple[int, ...]
    route_part: Optional[int]
    other: Hashable  # opaque identifier data

    @classmethod
    def from_route(cls, route: Route) -> "RouteDisc":
        points = route.get_scenario_points()
        return cls(
            train_name=route.route_kind,
            point_ids=tuple(point.point_id for point in points),
            route_part=route.route_part,
            other=(
                len(route.train_no),
                tuple((
                    point.point_id,
                    point.kind,
                    point.line,
                    point.stop_type == StopType.PH,
                ) for point in points),
            )
        )


@dataclasses.dataclass(frozen=True)
class Server:
    code: str
    name: str
    tz: int


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
        root_ctx: RootCtx,
):
    data = [{
        "no": format_route_no(route),
        "route_kind": route.route_kind,
        "start_time": route.get_start_time().strftime("%H:%M"),
        "duration": format_timedelta(
            route.end().get_exit_datetime()
            - route.start().get_entry_datetime()
        ),
        "train_type": route.train_type,
        "max_speed": max(
            (point.max_speed for point in route.get_scenario_points()),
            default=0
        ),
        "train_length": route.train_length,
        "train_weight": route.train_weight,
        "start_point": points[route.start().point_id].get_human_name(),
        "end_point": points[route.end().point_id].get_human_name(),
    } for route in sorted(routes, key=Route.get_start_time)]

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

    data = [{
        "prefixes": prefixes,
        "part": str(disc.route_part or ""),
        "kind": disc.train_name,
        "start": points[disc.point_ids[0]].get_human_name(),
        "end": points[disc.point_ids[-1]].get_human_name(),
        "duration": Range.from_minmax((
            r.end().get_exit_datetime() - r.start().get_entry_datetime()
            for r
            in groups[disc]
        ), fmt=format_timedelta),
        "types": sorted({TRAIN_TYPES[r.train_type] for r in groups[disc]}),
        "max_speed": Range.from_minmax(
            max(p.max_speed for p in r.get_scenario_points())
            for r
            in groups[disc]
        ),
        "train_length": Range.from_minmax(
            r.train_length for r in groups[disc]
        ),
        "train_weight": Range.from_minmax(
            r.train_weight for r in groups[disc]
        ),
        "routes": [{
            "start_time": route.get_start_time(),
            "number": format_route_no(route),
        } for route in sorted(groups[disc], key=Route.get_start_time)],
    } for disc, prefixes in sorted(prefixes.items(), key=lambda pair: (
        len(pair[1][0]),
        pair[1]
    ))]

    gen("route.html", destdir, name, root_ctx, {
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
        root_ctx: RootCtx,
):
    prev_no, next_no = adj
    params = {
        "train_number": route.train_no,
        "route_part": route.route_part or "",
        "kind": route.route_kind,
        "type": route.train_type,
        "length": route.train_length,
        "weight": route.train_weight,
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
        "server": server,
    })


def make_server(
        destdir: str,
        server: Server,
        routes: RawRoutes,
        root_ctx: RootCtx,
) -> set[str]:
    files = set()
    points = get_points(routes)
    routes = get_routes(routes, points)

    name = f"{server.code}/tt-by-start.html"
    gen_tt_by_start(server, destdir, name, points, routes, root_ctx)
    files.add(name)

    name = f"{server.code}/tt-by-route.html"
    adj = gen_tt_by_route(server, destdir, name, points, routes, root_ctx)
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

    for server in servers:
        path = os.path.join(cfg.src, "servers", f"{server.code}.json")
        tt = load(path, RawRoutes)
        server_files = make_server(cfg.dst, server, tt, root_ctx)
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


def make(src: str, dst: str, only_code: Optional[str]):
    cfg = GenConfig(src, dst)

    sync_ts = load(os.path.join(cfg.src, "meta.json"), Meta).sync_ts
    resources = get_resources(RESOURCES_VERSIONED)

    root_ctx = RootCtx(
        sync_ts=format_ts(sync_ts),
        resources=resources,
    )

    servers = load(os.path.join(cfg.src, "servers.json"), RawServers)

    servers = [
        Server(
            code=server.ServerCode,
            name=server.ServerName,
            tz=load(os.path.join(
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
