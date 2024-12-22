import dataclasses


COMPOSITION_SEP = ","


def serialize_composition(vehicles: list[str]) -> str:
    offenders = {vehicle for vehicle in vehicles if COMPOSITION_SEP in vehicle}
    if offenders:
        raise ValueError(f"separator in vehicle names: {offenders}")
    return COMPOSITION_SEP.join(vehicles)


def deserialize_composition(composition: str) -> list[str]:
    return composition.split(COMPOSITION_SEP)


@dataclasses.dataclass
class Train:
    server: str
    train_number: str
    composition: str
    vd_index: int
    first_seen: int
    first_seen_server: int
    last_seen: int
    last_seen_server: int
