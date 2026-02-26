import unittest
from itertools import chain

from more_itertools import duplicates_everseen

import consts
import db
import db.models


class TestConsts(unittest.TestCase):
    """consts.py consistency tests"""

    def test_points(self) -> None:
        duplicates = set(duplicates_everseen(chain.from_iterable(
            consts.DLC_POINTS.values()
        )))
        self.assertFalse(duplicates, "duplicate points")

    def test_controllable_points(self) -> None:
        shorts = set[str]()
        for dlc, points in consts.DLC_CONTROLLABLE_POINTS.items():
            for point, short in points.items():
                self.assertIn(point, consts.DLC_POINTS[dlc])
                self.assertNotIn(short, shorts, "duplicate short")
                shorts.add(short)

    def test_main_units(self) -> None:
        names = {details["name"] for details in consts.VEHICLES.values()}
        for name in consts.MAIN_UNITS.values():
            if name == "?":
                continue
            self.assertIn(name, names)

    def test_vehicles(self) -> None:
        families = set()
        for name, details in consts.VEHICLES.items():
            family = details["family"]
            self.assertIn(family, consts.VEHICLE_FAMILIES)
            families.add(family)
            self.assertNotIn(db.models.COMPOSITION_SEP, name)
        for family in consts.VEHICLE_FAMILIES:
            self.assertIn(family, families, "unused family")


class TestDb(unittest.TestCase):

    def test_split_stmts(self) -> None:
        stmts = db._split_stmts(
            "SELECT 1;\n"
            "\n"
            "SELECT -- 1; SELECT 1;\n"
            "       1;\n"
            "SELECT ';'\n"
            ";SELECT ';';SELECT 1;\n "
        )
        self.assertEqual(stmts, [
            "SELECT 1;",
            "SELECT -- 1; SELECT 1;\n       1;",
            "SELECT ';'\n;",
            "SELECT ';';",
            "SELECT 1;"
        ])

        for sql in "SELECT ';'\n", "SELECT 1; SELECT 1", "SELECT 1 --;":
            with self.assertRaises(ValueError):
                db._split_stmts(sql)
