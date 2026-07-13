# Legacy prototype references

This directory provides runnable copies of two useful ideas from the
repository's original prototype before the integrated SQLite application
replaced them:

- `tf_recommender/` is the original dependency-free term-frequency baseline.
- `sql_examples/queries.sql` contains the original standalone query examples.

The original files remain byte-for-byte at `../ai_recommender/` and
`../backend/`. These copies are not used by the current API. The JSON sample's
invalid SQL-style header was removed in this copy so the baseline can still be
executed. No publication dates or article claims were added or changed.

Run the historical recommender from the repository root with:

```bash
python legacy/tf_recommender/recommender.py "king pawn endgames"
```
