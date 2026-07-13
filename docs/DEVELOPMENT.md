# Development guide

## Local loop

```bash
make check
make dev
```

The Make targets create `instance/chesslife.sqlite3`. Delete only that local database when testing a migration from an empty state:

```bash
make clean-db
python -m chesslife_demo init-db
```

## Adding a migration

1. Add a numbered `.sql` file to `chesslife_demo/migrations/`.
2. Never edit a migration that may already have been applied.
3. Make the change compatible with SQLite.
4. Add a database or repository regression test.
5. Run `make check` and build the container.

The migration runner records filenames, so use a stable numeric prefix such as `003_add_reading_time.sql`.

## Frontend rules

- Keep the app dependency-free unless a concrete product need justifies a build tool.
- Render API strings through `textContent`, form properties, or DOM attributes—not HTML parsing APIs.
- Preserve visible labels, keyboard focus, live loading/error status, and reduced-motion behavior.
- Use same-origin `/api/...` paths so local, container, and hosted environments behave consistently.

## Test layout

- `test_database.py`: migration, constraint, and FTS trigger behavior
- `test_repository.py`: search/filter/detail/recommendation behavior
- `test_server.py`: real HTTP requests against an ephemeral port and database
- `test_frontend.py`: safe-rendering and accessibility contracts

All tests use temporary SQLite databases and leave the working tree unchanged.
