from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class FrontendTests(unittest.TestCase):
    def test_javascript_uses_safe_dom_apis(self) -> None:
        source = (ROOT / "chesslife_demo" / "static" / "app.js").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("innerHTML", source)
        self.assertNotIn("insertAdjacentHTML", source)
        self.assertIn("textContent", source)
        self.assertIn("replaceChildren", source)

    def test_accessibility_landmarks_and_live_regions_exist(self) -> None:
        html = (ROOT / "chesslife_demo" / "static" / "index.html").read_text(
            encoding="utf-8"
        )

        for marker in (
            'href="#main-content"',
            'role="search"',
            'aria-live="polite"',
            '<dialog id="article-dialog"',
            'label for="search-input"',
        ):
            self.assertIn(marker, html)


if __name__ == "__main__":
    unittest.main()
