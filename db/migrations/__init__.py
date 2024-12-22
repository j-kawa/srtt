import dataclasses
import os


@dataclasses.dataclass(frozen=True)
class Migration:
    ver: int
    name: str

    def get_sql(self) -> str:
        path = os.path.join(
            os.path.dirname(__file__),
            self.name + ".sql",
        )
        with open(path, "r") as f:
            return f.read()


MIGRATIONS = [
    Migration(1, "01-init"),
]
