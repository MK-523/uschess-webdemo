from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from chesslife_demo.database import Database
from chesslife_demo.server import create_server


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        database = Database(Path(cls.temp_dir.name) / "server.sqlite3")
        cls.server = create_server(database, host="127.0.0.1", port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address[:2]
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)
        cls.temp_dir.cleanup()

    def request(self, path: str):
        return urllib.request.urlopen(f"{self.base_url}{path}", timeout=3)

    def test_health_and_security_headers(self) -> None:
        with self.request("/api/health") as response:
            payload = json.load(response)
            headers = response.headers

        self.assertEqual(payload, {"status": "ok"})
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_publication_search_detail_and_recommendations(self) -> None:
        with self.request("/api/publications?q=endgame") as response:
            search = json.load(response)
        with self.request("/api/publications/2") as response:
            detail = json.load(response)
        with self.request("/api/publications/2/recommendations") as response:
            recommendations = json.load(response)

        self.assertEqual(search["total"], 1)
        self.assertEqual(detail["title"], "Basic King and Pawn Endgames")
        self.assertEqual(len(recommendations["items"]), 3)

    def test_invalid_route_returns_json_404(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as caught:
            self.request("/api/unknown")

        self.assertEqual(caught.exception.code, 404)
        payload = json.loads(caught.exception.read())
        self.assertEqual(payload["error"], "API route not found")

    def test_static_home_is_served_with_csp(self) -> None:
        with self.request("/") as response:
            body = response.read().decode("utf-8")

        self.assertIn("ChessLife Discovery Demo", body)
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")


if __name__ == "__main__":
    unittest.main()

