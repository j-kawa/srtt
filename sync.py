import json
import os
from typing import Any, Optional

from external.client import ApiClient
from external.models import Meta
from utils import pick_codes, time_secs


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


def sync(api: ApiClient, dst: str, only_code: Optional[str]):
    saver = Saver(dst)

    meta = Meta(sync_ts=time_secs())
    saver.save_json(["meta.json"], meta.model_dump())

    servers = api.get_servers()
    saver.save_json(["servers.json"], servers.model_dump())

    all_codes = [server.ServerCode for server in servers.root]
    codes = pick_codes(only_code, all_codes)

    for code in codes:
        routes = api.get_routes(code)
        saver.save_json(["servers", f"{code}.json"], routes.model_dump())
        timezone = api.get_timezone(code)
        saver.save_json(["timezones", f"{code}.json"], timezone)
