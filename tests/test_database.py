from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from chesslife_demo.database import Database


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database = Database(Path(self.temp_dir.name) / "test.sqlite3")

    def test_migrations_are_idempotent_and_seed_existing_dates(self) -> None:
        first = self.database.initialize()
        second = self.database.initialize()

        self.assertEqual(first, ["001_schema.sql", "002_demo_seed.sql"])
        self.assertEqual(second, [])
        with self.database.connect() as connection:
            count = connection.execute("SELECT COUNT(*) FROM publications").fetchone()[0]
            dates = [
                row[0]
                for row in connection.execute(
                    "SELECT publication_date FROM publications ORDER BY publication_id"
                )
            ]
        self.assertEqual(count, 5)
        self.assertEqual(
            dates,
            ["2024-11-01", "2025-01-10", "2024-08-19", "1993-07-22", "2025-02-14"],
        )

    def test_foreign_keys_are_enforced_for_every_connection(self) -> None:
        self.database.initialize()
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO publications(
                        title, content, author_id, category_id, publication_date, summary
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ("Invalid", "Invalid", 999, 1, "2025-01-01", "Invalid"),
                )

    def test_fts_index_stays_in_sync_after_updates(self) -> None:
        self.database.initialize()
        with self.database.connect() as connection:
            connection.execute(
                "UPDATE publications SET title = ? WHERE publication_id = 1",
                ("Najdorf Field Guide",),
            )
        with self.database.connect() as connection:
            result = connection.execute(
                """
                SELECT rowid FROM publications_fts
                WHERE publications_fts MATCH 'najdorf'
                """
            ).fetchall()
        self.assertEqual([row[0] for row in result], [1])


if __name__ == "__main__":
    unittest.main()

