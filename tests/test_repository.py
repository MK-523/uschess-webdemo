from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from chesslife_demo.database import Database
from chesslife_demo.repository import PublicationQuery, PublicationRepository


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        database = Database(Path(self.temp_dir.name) / "test.sqlite3")
        database.initialize()
        self.repository = PublicationRepository(database)

    def test_default_search_is_newest_first(self) -> None:
        result = self.repository.search(PublicationQuery())

        self.assertEqual(result["total"], 5)
        self.assertEqual(result["items"][0]["title"], "Practical Middlegame Plans")
        self.assertFalse(result["has_more"])

    def test_fts_search_supports_prefixes_and_plain_user_punctuation(self) -> None:
        result = self.repository.search(PublicationQuery(query="endgam!!!"))

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["publication_id"], 2)

    def test_filters_and_pagination_compose(self) -> None:
        result = self.repository.search(
            PublicationQuery(
                category="Openings",
                date_from="2024-01-01",
                date_to="2025-12-31",
                limit=1,
            )
        )

        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["items"]), 1)
        self.assertTrue(result["has_more"])

        next_page = self.repository.search(
            PublicationQuery(category="Openings", limit=1, offset=1)
        )
        self.assertNotEqual(
            result["items"][0]["publication_id"],
            next_page["items"][0]["publication_id"],
        )

    def test_detail_and_missing_publication(self) -> None:
        publication = self.repository.get(2)

        self.assertEqual(publication["author"], "GM Anna")
        self.assertIn("illustrative positions", publication["content"])
        self.assertIsNone(self.repository.get(999))

    def test_related_results_exclude_source_and_favor_same_category(self) -> None:
        related = self.repository.related(1, limit=3)

        self.assertNotIn(1, [item["publication_id"] for item in related])
        self.assertEqual(related[0]["publication_id"], 5)
        self.assertGreater(related[0]["recommendation_score"], 0.35)

    def test_query_recommendations_are_deterministic(self) -> None:
        first = self.repository.recommend_for_query("Sicilian plans", limit=3)
        second = self.repository.recommend_for_query("Sicilian plans", limit=3)

        self.assertEqual(first, second)
        self.assertEqual(first[0]["publication_id"], 1)
        self.assertEqual(self.repository.recommend_for_query("!!!"), [])


if __name__ == "__main__":
    unittest.main()

