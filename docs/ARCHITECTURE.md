# Architecture

## Boundaries

The application has four intentionally small boundaries:

1. `chesslife_demo/static/` owns presentation, filter state, API requests, and accessible interactions.
2. `server.py` translates HTTP routes and bounded query parameters into repository calls.
3. `repository.py` owns parameterized SQL, result shapes, and recommendation ranking.
4. `database.py` owns connections, foreign-key enforcement, and atomic forward migrations.

The HTTP server and frontend share an origin. No CORS policy or client-side API host configuration is needed.

## Search

SQLite FTS5 indexes title, summary, and content through an external-content virtual table. Insert, update, and delete triggers keep the search index synchronized with the relational publication table.

User search text is reduced to lowercase alphanumeric tokens. Each token becomes an FTS prefix term, matching any supplied term, and at most 12 terms are accepted. Other filters remain normal SQL parameters. Search results use FTS5's `bm25` order, with publication date and ID as deterministic tie-breakers.

## Recommendations

Related reading is deliberately explainable. The repository builds a token set from the selected article and each candidate, calculates Jaccard overlap, and adds a fixed same-category bonus. It then sorts by score, date, and ID.

This is appropriate for demonstrating the product flow with five fictional records. It is not evidence that the approach would rank a real archive well.

## Database lifecycle

Packaged migrations in `chesslife_demo/migrations/` are sorted by filename and recorded in `schema_migrations`. Each pending script and its migration record run in one `BEGIN IMMEDIATE` transaction. Startup applies only missing migrations, so repeated initialization is safe.

`002_demo_seed.sql` contains the original five fictional publication dates:

- 2024-11-01
- 2025-01-10
- 2024-08-19
- 1993-07-22
- 2025-02-14

No new publication dates were introduced during the rebuild.

## Security posture

- Every SQL value is bound as a parameter.
- Search grammar is generated from accepted tokens rather than passed directly to FTS5.
- The browser creates elements and writes untrusted strings through `textContent`; it does not render publication fields as HTML.
- API lengths and pagination bounds are enforced server-side.
- Static and API responses include CSP, frame, content-type, referrer, and permissions headers.
- The server exposes read-only GET routes and binds to loopback by default outside Docker.

This is still a portfolio demo. Authentication, authoring, audit logs, rate limiting, backups, and production observability would be separate deployment requirements.
