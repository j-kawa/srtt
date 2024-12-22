__version__ = "0.2"

import argparse

from db import Database, migrate
from external.client import ApiClient
from makesite import make
from scan import scan
from sync import sync


COMMANDS = ["migrate", "sync", "scan", "make"]


parser = argparse.ArgumentParser(
    description="SimRail timetable generator",
    allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "-V",
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
)
parser.add_argument(
    "command",
    type=str,
    nargs="+",
    metavar="command",
    choices=COMMANDS,
    help=f"one of: {', '.join(COMMANDS)}",
)
parser.add_argument(
    "-r",
    type=str,
    dest="raw_dir",
    metavar="dir",
    help="SimRail APIs data directory",
    default="raw",
)
parser.add_argument(
    "-o",
    type=str,
    dest="output_dir",
    metavar="dir",
    help="static files output directory",
    default="output",
)
parser.add_argument(
    "-c",
    type=str,
    dest="code",
    metavar="code",
    help="limit to single server",
    default=None,
)
parser.add_argument(
    "-d",
    type=str,
    dest="db",
    metavar="path",
    help="running trains history database path",
    default="trains.db",
)
parser.add_argument(
    "-t",
    type=float,
    dest="request_interval",
    metavar="seconds",
    help="minimum interval between requests",
    default=1.0,
)


def main():
    args = parser.parse_args()

    with (
            ApiClient(
                interval=args.request_interval,
                user_agent=f"srtt/{__version__}"
            ) as api,
            Database(args.db) as db,
    ):
        if "migrate" in args.command:
            migrate(db)
        if "scan" in args.command:
            scan(db, api, args.code)
        if "sync" in args.command:
            sync(api, args.raw_dir, args.code)
        if "make" in args.command:
            make(db, args.raw_dir, args.output_dir, args.code)


if __name__ == "__main__":
    main()
