import dataclasses
import re

from consts import VEHICLE_FAMILIES, VEHICLES


@dataclasses.dataclass
class Vehicle:
    name: str
    weight: float
    length: float
    type_: str


IDENT_REGEX = re.compile(
    r"(?P<model>[-\w/ ]+)"
    r"(:(?P<brake>[A-Z][A-Z\d]*?))?"
    r"(:(?P<cargo_weight>\d*))?"
    r"(@(?P<cargo>[-\w]*))?"
)


def parse_ident(ident: str) -> tuple[str, int]:
    ident = ident.strip()
    if match_ := IDENT_REGEX.fullmatch(ident):
        groups = match_.groupdict()
        return groups["model"], int(groups["cargo_weight"] or "0")
    raise ValueError(f"unrecognized format: {repr(ident)}")


def parse_vehicle(ident: str) -> Vehicle:
    model, cargo_weight = parse_ident(ident)
    vehicle = VEHICLES[model]
    details = VEHICLE_FAMILIES[vehicle["family"]]
    return Vehicle(
        name=vehicle["name"],
        weight=details["weight"] + cargo_weight,
        length=details["length"],
        type_=details["type"]
    )
