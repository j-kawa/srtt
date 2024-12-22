import time
from datetime import datetime
from typing import Optional


def pick_codes(only_code: Optional[str], all_codes: list[str]) -> list[str]:
    if not only_code:
        return all_codes
    if only_code not in all_codes:
        raise ValueError(f"code `{only_code}` doesn't match any server")
    return [only_code]


def parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if ts is None:
        return None
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


def time_secs() -> int:
    return time.time_ns() // 1_000_000_000


def time_millis() -> int:
    return time.time_ns() // 1_000_000
