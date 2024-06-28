__version__ = "0.1"

import argparse

from makesite import make
from sync import sync


COMMANDS = ["sync", "make"]


parser = argparse.ArgumentParser(
    description="SimRail timetable generator",
    allow_abbrev=False,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.version = f"{parser.prog} {__version__}"
parser.add_argument(
    "-V",
    "--version",
    action="version"
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


def main():
    args = parser.parse_args()
    if "sync" in args.command:
        sync(args.raw_dir, args.code)
    if "make" in args.command:
        make(args.raw_dir, args.output_dir, args.code)


if __name__ == "__main__":
    main()
