from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .database import Database


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
MAX_PAGE_SIZE = 50


@dataclass(frozen=True)
class PublicationQuery:
    query: str = ""
    category: str = ""
    date_from: str = ""
    date_to: str = ""
    limit: int = 12
    offset: int = 0


def _tokens(text: str) -> set[str]:
    return set(TOKEN_PATTERN.findall(text.lower()))


def _fts_query(text: str) -> str:
    tokens = TOKEN_PATTERN.findall(text.lower())[:12]
    return " OR ".join(f'"{token}"*' for token in tokens)


def _publication_dict(row: Any, include_content: bool = False) -> dict[str, Any]:
    result = {
        "publication_id": row["publication_id"],
        "title": row["title"],
        "summary": row["summary"],
        "publication_date": row["publication_date"],
        "author": row["author"],
        "category": row["category"],
    }
    if include_content:
        result["content"] = row["content"]
    return result


class PublicationRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def categories(self) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT c.name, COUNT(p.publication_id) AS publication_count
                FROM categories AS c
                LEFT JOIN publications AS p ON p.category_id = c.category_id
                GROUP BY c.category_id, c.name
                ORDER BY c.name COLLATE NOCASE
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def search(self, filters: PublicationQuery) -> dict[str, Any]:
        limit = min(MAX_PAGE_SIZE, max(1, filters.limit))
        offset = max(0, filters.offset)
        clauses: list[str] = []
        params: list[Any] = []
        fts = _fts_query(filters.query)

        if fts:
            clauses.append("publications_fts MATCH ?")
            params.append(fts)
        if filters.category:
            clauses.append("c.name = ?")
            params.append(filters.category)
        if filters.date_from:
            clauses.append("p.publication_date >= ?")
            params.append(filters.date_from)
        if filters.date_to:
            clauses.append("p.publication_date <= ?")
            params.append(filters.date_to)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        order = (
            "ORDER BY bm25(publications_fts) ASC, p.publication_date DESC, "
            "p.publication_id DESC"
            if fts
            else "ORDER BY p.publication_date DESC, p.publication_id DESC"
        )

        fts_join = (
            "JOIN publications_fts ON publications_fts.rowid = p.publication_id"
            if fts
            else ""
        )
        base = f"""
            FROM publications AS p
            JOIN authors AS a ON a.author_id = p.author_id
            JOIN categories AS c ON c.category_id = p.category_id
            {fts_join}
        """
        with self.database.connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) {base} {where}", params
            ).fetchone()[0]
            rows = connection.execute(
                f"""
                SELECT p.publication_id, p.title, p.summary, p.publication_date,
                       a.name AS author, c.name AS category
                {base}
                {where}
                {order}
                LIMIT ? OFFSET ?
                """,
                [*params, limit, offset],
            ).fetchall()

        return {
            "items": [_publication_dict(row) for row in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(rows) < total,
        }

    def get(self, publication_id: int) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT p.publication_id, p.title, p.summary, p.content,
                       p.publication_date, a.name AS author, c.name AS category
                FROM publications AS p
                JOIN authors AS a ON a.author_id = p.author_id
                JOIN categories AS c ON c.category_id = p.category_id
                WHERE p.publication_id = ?
                """,
                (publication_id,),
            ).fetchone()
        return _publication_dict(row, include_content=True) if row else None

    def related(self, publication_id: int, limit: int = 3) -> list[dict[str, Any]]:
        source = self.get(publication_id)
        if source is None:
            return []

        limit = min(10, max(1, limit))
        source_terms = _tokens(
            f"{source['title']} {source['summary']} {source['content']}"
        )
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT p.publication_id, p.title, p.summary, p.content,
                       p.publication_date, a.name AS author, c.name AS category
                FROM publications AS p
                JOIN authors AS a ON a.author_id = p.author_id
                JOIN categories AS c ON c.category_id = p.category_id
                WHERE p.publication_id != ?
                """,
                (publication_id,),
            ).fetchall()

        ranked: list[tuple[float, str, int, Any]] = []
        for row in rows:
            candidate_terms = _tokens(
                f"{row['title']} {row['summary']} {row['content']}"
            )
            union = source_terms | candidate_terms
            overlap = len(source_terms & candidate_terms) / len(union) if union else 0
            category_bonus = 0.35 if row["category"] == source["category"] else 0
            score = overlap + category_bonus
            ranked.append(
                (score, row["publication_date"], row["publication_id"], row)
            )

        ranked.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        results: list[dict[str, Any]] = []
        for score, _, _, row in ranked[:limit]:
            item = _publication_dict(row)
            item["recommendation_score"] = round(score, 4)
            results.append(item)
        return results

    def recommend_for_query(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not _tokens(query):
            return []
        result = self.search(PublicationQuery(query=query, limit=limit))
        return result["items"]
