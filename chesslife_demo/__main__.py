from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .database import Database
from .repository import PublicationRepository
from .server import create_server


DEFAULT_DB_PATH = Path(
    os.environ.get(
        "CHESSLIFE_DB_PATH", Path.home() / ".chesslife-demo" / "chesslife.sqlite3"
    )
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and maintain the ChessLife publication discovery demo."
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    subparsers = parser.add_subparsers(dest="command")

    serve = subparsers.add_parser("serve", help="Start the API and static site")
    serve.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    serve.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))

    subparsers.add_parser("init-db", help="Apply pending database migrations")

    recommend = subparsers.add_parser(
        "recommend", help="Print recommendations for a natural-language query"
    )
    recommend.add_argument("query")
    recommend.add_argument("--limit", type=int, default=5)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    command = args.command or "serve"
    database = Database(args.db)

    if command == "init-db":
        applied = database.initialize()
        if applied:
            print("Applied migrations:", ", ".join(applied))
        else:
            print("Database is up to date.")
        return 0

    if command == "recommend":
        database.initialize()
        items = PublicationRepository(database).recommend_for_query(
            args.query, max(1, min(10, args.limit))
        )
        print(json.dumps(items, indent=2, ensure_ascii=False))
        return 0

    host = getattr(args, "host", os.environ.get("HOST", "127.0.0.1"))
    port = getattr(args, "port", int(os.environ.get("PORT", "8000")))
    server = create_server(database, host, port)
    actual_host, actual_port = server.server_address[:2]
    print(f"ChessLife demo listening on http://{actual_host}:{actual_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
