from typing import Optional

from db import Database, Transaction
from db.expr import All, Desc, Eq, Field, Value
from db.models import Train, serialize_composition
from external.client import ApiClient
from external.models import RawTrain
from utils import pick_codes, time_secs


def get_last_train(
        tx: Transaction,
        server: str,
        train_number: str,
) -> Optional[tuple[int, Train]]:
    trains = tx.select(
        model=Train,
        where=All(
            Eq(Field("server"), Value(server)),
            Eq(Field("train_number"), Value(train_number)),
        ),
        order=[Desc("last_seen")],
        limit=1,
    )
    return next(iter(trains), None)


def train_is_new(current: Train, previous: Train) -> bool:
    if current.composition != previous.composition:
        return True
    if current.first_seen - previous.last_seen >= 12 * 3600:  # 12 hours
        return True
    return False


def update_trains(
        tx: Transaction,
        raw_trains: list[RawTrain],
        code: str,
        world_time: int,
        server_time: int,
) -> None:
    for raw_train in raw_trains:
        train = Train(
            server=code,
            train_number=raw_train.TrainNoLocal,
            composition=serialize_composition(raw_train.Vehicles),
            vd_index=raw_train.TrainData.VDDelayedTimetableIndex,
            first_seen=world_time,
            last_seen=world_time,
            first_seen_server=server_time,
            last_seen_server=server_time,
        )
        last = get_last_train(tx, train.server, train.train_number)
        if last is None:
            tx.insert(train)
            continue
        id_, last_train = last
        if train_is_new(train, last_train):
            tx.insert(train)
            continue
        tx.update(
            model=Train,
            values={
                "vd_index": train.vd_index,
                "last_seen": train.last_seen,
                "last_seen_server": train.last_seen_server,
            },
            where=Eq(Field("id"), Value(id_)),
        )


def scan(db: Database, api: ApiClient, only_code: Optional[str]) -> None:
    servers = api.get_servers()
    all_codes = [server.ServerCode for server in servers.root]
    codes = pick_codes(only_code, all_codes)

    for code in codes:
        world_time = time_secs()
        server_time = api.get_time(code) // 1_000
        trains = api.get_trains(code)

        with db.transaction(exclusive=True) as tx:
            update_trains(
                tx,
                trains.root,
                code,
                world_time,
                server_time,
            )
