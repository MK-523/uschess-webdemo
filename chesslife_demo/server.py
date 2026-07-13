from __future__ import annotations

import json
import mimetypes
import re
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .database import Database
from .repository import PublicationQuery, PublicationRepository


PUBLICATION_PATH = re.compile(r"^/api/publications/(\d+)$")
RECOMMENDATION_PATH = re.compile(r"^/api/publications/(\d+)/recommendations$")


def _first(params: dict[str, list[str]], key: str, default: str = "") -> str:
    return params.get(key, [default])[0].strip()


def _bounded_int(
    params: dict[str, list[str]], key: str, default: int, minimum: int, maximum: int
) -> int:
    try:
        value = int(_first(params, key, str(default)))
    except ValueError:
        return default
    return min(maximum, max(minimum, value))


class ChessLifeRequestHandler(SimpleHTTPRequestHandler):
    server_version = "ChessLifeDemo/1.0"

    def __init__(
        self,
        *args: Any,
        repository: PublicationRepository,
        static_dir: Path,
        **kwargs: Any,
    ) -> None:
        self.repository = repository
        super().__init__(*args, directory=str(static_dir), **kwargs)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
        )
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._handle_api(parsed.path, parse_qs(parsed.query))
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def _handle_api(self, path: str, params: dict[str, list[str]]) -> None:
        try:
            if path == "/api/health":
                self._json_response({"status": "ok"})
                return
            if path == "/api/categories":
                self._json_response({"items": self.repository.categories()})
                return
            if path == "/api/publications":
                filters = PublicationQuery(
                    query=_first(params, "q")[:200],
                    category=_first(params, "category")[:100],
                    date_from=_first(params, "date_from")[:10],
                    date_to=_first(params, "date_to")[:10],
                    limit=_bounded_int(params, "limit", 12, 1, 50),
                    offset=_bounded_int(params, "offset", 0, 0, 100_000),
                )
                self._json_response(self.repository.search(filters))
                return
            if path == "/api/recommendations":
                query = _first(params, "q")[:200]
                limit = _bounded_int(params, "limit", 5, 1, 10)
                self._json_response(
                    {"items": self.repository.recommend_for_query(query, limit)}
                )
                return

            recommendation_match = RECOMMENDATION_PATH.fullmatch(path)
            if recommendation_match:
                publication_id = int(recommendation_match.group(1))
                if self.repository.get(publication_id) is None:
                    self._error_response(HTTPStatus.NOT_FOUND, "Publication not found")
                    return
                limit = _bounded_int(params, "limit", 3, 1, 10)
                self._json_response(
                    {"items": self.repository.related(publication_id, limit)}
                )
                return

            publication_match = PUBLICATION_PATH.fullmatch(path)
            if publication_match:
                publication = self.repository.get(int(publication_match.group(1)))
                if publication is None:
                    self._error_response(HTTPStatus.NOT_FOUND, "Publication not found")
                    return
                self._json_response(publication)
                return
            self._error_response(HTTPStatus.NOT_FOUND, "API route not found")
        except Exception as exc:
            self.log_error("Unhandled API error: %s", exc)
            self._error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR, "The server could not complete the request"
            )

    def _json_response(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error_response(self, status: HTTPStatus, message: str) -> None:
        self._json_response({"error": message}, status)

    def guess_type(self, path: str) -> str:
        return mimetypes.guess_type(path)[0] or "application/octet-stream"


def create_server(
    database: Database,
    host: str = "127.0.0.1",
    port: int = 8000,
    static_dir: str | Path = Path(__file__).resolve().parent / "static",
) -> ThreadingHTTPServer:
    database.initialize()
    repository = PublicationRepository(database)
    handler = partial(
        ChessLifeRequestHandler,
        repository=repository,
        static_dir=Path(static_dir),
    )
    return ThreadingHTTPServer((host, port), handler)
