from __future__ import annotations

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


class Database:
    """Owns connections and forward-only SQL migrations for the demo database."""

    def __init__(
        self,
        path: str | Path,
        migrations_dir: str | Path = DEFAULT_MIGRATIONS_DIR,
    ) -> None:
        self.path = Path(path)
        self.migrations_dir = Path(migrations_dir)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def migrate(self) -> list[str]:
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        if not migration_files:
            raise RuntimeError(f"No SQL migrations found in {self.migrations_dir}")

        applied: list[str] = []
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            existing = {
                row["version"]
                for row in connection.execute("SELECT version FROM schema_migrations")
            }
            for migration_file in migration_files:
                version = migration_file.name
                if version in existing:
                    continue
                sql = migration_file.read_text(encoding="utf-8")
                escaped_version = version.replace("'", "''")
                connection.executescript(
                    "BEGIN IMMEDIATE;\n"
                    f"{sql}\n"
                    "INSERT INTO schema_migrations(version) "
                    f"VALUES ('{escaped_version}');\n"
                    "COMMIT;"
                )
                applied.append(version)
        return applied

    def initialize(self) -> list[str]:
        return self.migrate()
