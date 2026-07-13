# Historical artifact boundary

The repository began as three disconnected examples:

- `frontend/` contained a static publication-search page and local data file.
- `backend/` contained standalone schema, seed, and query examples.
- `ai_recommender/` contained a dependency-free term-frequency script.

Those original files remain at those paths byte-for-byte. This preserves old repository links and makes it possible to inspect the actual starting point. They are not the supported runtime: the original `.json` files include SQL-style leading comments, the old SQL seed has an unresolved author reference, and the original browser page is not connected to an API.

The supported application is entirely under `chesslife_demo/`. It carries forward only the five fictional sample publications and the five publication dates already present in the original SQL seed. Its migrations reconcile the missing author record, and its packaged static interface calls the new read-only API.

`legacy/` contains normalized, runnable copies of the useful term-frequency and query baselines. Their role is comparison, not production execution.

This split is deliberate:

| Location | Status | Used at runtime |
| --- | --- | --- |
| `chesslife_demo/` | Supported integrated demo | Yes |
| `tests/`, `docs/`, container and CI files | Supported development tooling | Yes |
| `frontend/`, `backend/`, `ai_recommender/` | Byte-for-byte original artifacts | No |
| `legacy/` | Runnable historical references | No |

