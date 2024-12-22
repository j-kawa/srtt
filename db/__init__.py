import dataclasses
import sqlite3
from types import TracebackType
from typing import TYPE_CHECKING, Optional, Type, TypeVar

from pydantic import TypeAdapter

from .expr import Expr, Order, Param
from .migrations import MIGRATIONS


if TYPE_CHECKING:
    from _typeshed import DataclassInstance


M = TypeVar("M", bound="DataclassInstance")


def _get_table_fields(model: Type[M]) -> tuple[str, list[str]]:
    return (
        model.__name__.lower(),
        [f.name for f in dataclasses.fields(model)]
    )


def _split_stmts(sql: str) -> list[str]:
    ret = []

    search_start = 0
    stmt_start = 0

    while True:
        end = sql.find(";", search_start) + 1
        if not end:
            if sql[stmt_start:].strip():
                # fixme: sql='SELECT 1;\n--'
                raise ValueError("incomplete input")
            break
        stmt = sql[stmt_start:end]
        search_start = end
        if not sqlite3.complete_statement(stmt):
            continue
        ret.append(stmt.lstrip())
        stmt_start = end

    return ret


class Transaction:

    def __init__(self, cur: sqlite3.Cursor):
        self._cur = cur

    def select(
            self,
            model: Type[M],
            where: Optional[Expr] = None,
            order: Optional[list[Order]] = None,
            limit: Optional[int] = None,
    ) -> list[tuple[int, M]]:
        table, fields = _get_table_fields(model)

        params: list[Param] = []
        sql = " ".join(filter(None, (
            f"SELECT id, {', '.join(fields)} FROM {table}",
            where and "WHERE " + where.to_sql(params) or "",
            order and "ORDER BY " + ", ".join(o.to_sql() for o in order) or "",
            limit is not None and f"LIMIT {limit}" or "",
        )))

        ta = TypeAdapter(model)
        return [
            (int(id_), ta.validate_python(model(*row), strict=True))
            for id_, *row
            in self._cur.execute(sql, params)
        ]

    def insert(self, obj: M) -> None:
        table, fields = _get_table_fields(obj.__class__)

        sql = (
            f"INSERT INTO {table}({', '.join(fields)}) "
            f"VALUES ({', '.join('?' for _ in fields)}) "
        )
        params = dataclasses.astuple(obj)

        self._cur.execute(sql, params)

    def update(
            self,
            model: type[M],
            values: dict[str, Param],
            where: Optional[Expr] = None,
    ) -> None:
        if not values:
            return
        table, _ = _get_table_fields(model)
        fields = list(values)

        params = [values[field] for field in fields]
        sql = " ".join(filter(None, [
            f"UPDATE {table} "
            f"SET {', '.join(f'{field} = ?' for field in fields)}",
            where and "WHERE " + where.to_sql(params) or "",
        ]))
        self._cur.execute(sql, params)

    def run_script(self, sql: str) -> None:
        # cur.executescript(sql) doesn't respect the isolation_level
        for stmt in _split_stmts(sql):
            self._cur.execute(stmt)

    def get_user_version(self) -> int:
        (version,), = self._cur.execute("PRAGMA user_version")
        return int(version)

    def set_user_version(self, ver: int) -> None:
        self._cur.execute(f"PRAGMA user_version = {ver}")


class TransactionManager:

    def __init__(self, conn: sqlite3.Connection, exclusive: bool):
        self._cur = conn.cursor()
        self.exclusive = exclusive

    def __enter__(self) -> Transaction:
        self._cur.execute("BEGIN EXCLUSIVE" if self.exclusive else "BEGIN")
        return Transaction(self._cur)

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        self._cur.execute("COMMIT" if exc_type is None else "ROLLBACK")
        self._cur.close()


class Database:

    def __init__(self, path: str, trace: bool = False):
        # todo: change in python 3.12
        self._conn = sqlite3.connect(path, isolation_level=None)
        if trace:
            self._conn.set_trace_callback(print)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def transaction(self, exclusive: bool = False) -> TransactionManager:
        return TransactionManager(self._conn, exclusive)


def migrate(db: Database) -> None:
    with db.transaction(exclusive=True) as tx:
        version = tx.get_user_version()
        for migration in MIGRATIONS:
            if migration.ver <= version:
                continue
            print("applying migration", migration.name)
            sql = migration.get_sql()
            tx.run_script(sql)
            tx.set_user_version(migration.ver)
