# API reference

All API routes are read-only and return JSON. Error responses use the shape:

```json
{"error": "Human-readable message"}
```

## Health

`GET /api/health`

```json
{"status": "ok"}
```

## Categories

`GET /api/categories`

Returns categories alphabetically with the number of publications assigned to each category.

## Publication search

`GET /api/publications`

| Parameter | Meaning | Bound |
| --- | --- | --- |
| `q` | Full-text terms matched as case-insensitive token prefixes | First 200 characters and 12 tokens |
| `category` | Exact category name | First 100 characters |
| `date_from` | Inclusive lower publication date | `YYYY-MM-DD` |
| `date_to` | Inclusive upper publication date | `YYYY-MM-DD` |
| `limit` | Page size | 1–50; default 12 |
| `offset` | Result offset | 0–100,000 |

Example:

```text
/api/publications?q=endgame&category=Endgames&date_from=2024-01-01
```

Response fields include `items`, `total`, `limit`, `offset`, and `has_more`. Query text is tokenized before it reaches FTS5; category and date values use parameterized SQL.

## Publication detail

`GET /api/publications/{id}`

Returns metadata plus the complete fictional demo body. Unknown numeric IDs return `404`.

## Related publications

`GET /api/publications/{id}/recommendations?limit=3`

The deterministic score is:

```text
Jaccard token overlap + 0.35 when categories match
```

The source publication is always excluded. Ties are resolved by publication date and numeric ID, which makes results reproducible.

## Query recommendations

`GET /api/recommendations?q=endgame+practice&limit=5`

This is a small convenience wrapper around the FTS search. Empty or punctuation-only queries return an empty list rather than the full archive.

