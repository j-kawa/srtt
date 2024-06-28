import json
import os
import time
from typing import Any, Optional

from external.fetch import get_routes, get_servers, get_timezone
from external.models import Meta
from utils import pick_codes


class Saver:

    def __init__(self, directory: str):
        self.directory = directory
        self.mkdir_cache = set()

    def _ensure_dir_exists(self, path: str):
        if path in self.mkdir_cache:
            return
        os.makedirs(path, exist_ok=True)
        self.mkdir_cache.add(path)

    def save_json(self, path_parts: list[str], obj: Any):
        path = os.path.join(self.directory, *path_parts)
        self._ensure_dir_exists(os.path.dirname(path))
        print("SAVE", path)
        with open(path, "wt") as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)


def sync(dst: str, only_code: Optional[str]):
    saver = Saver(dst)

    meta = Meta(sync_ts=time.time_ns() // 10**9)
    saver.save_json(["meta.json"], meta.model_dump())

    servers = get_servers()
    saver.save_json(["servers.json"], servers.model_dump())

    all_codes = [server.ServerCode for server in servers.root]
    codes = pick_codes(only_code, all_codes)

    for code in codes:
        routes = get_routes(code)
        saver.save_json(["servers", f"{code}.json"], routes.model_dump())
        timezone = get_timezone(code)
        saver.save_json(["timezones", f"{code}.json"], timezone)
