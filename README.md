# ChessLife Web Demo

A public, scaled-down reconstruction of selected publication-search components from web work associated with ChessLife.

The repository demonstrates three pieces of a small publication-discovery stack:

- a static browser interface for listing and searching publications;
- an example SQL schema with seed data;
- a lightweight Python recommender based on keyword and term-frequency matching.

This is a portfolio demonstration. It is not the production ChessLife codebase and does not contain production data.

## Repository structure

```text
frontend/        static HTML, CSS, JavaScript, and local publication data
backend/         example SQL schema, seed data, and queries
ai_recommender/  keyword/term-frequency recommender and sample article JSON
```

## Quick start

### Frontend

Open [`frontend/index.html`](frontend/index.html) in a browser. The page reads the local JSON data included with the demo.

### Recommender

The recommender uses Python 3.8+ and no external Python libraries.

```bash
cd ai_recommender
python3 recommender.py "I want endgame practice"
```

It compares the query against the sample articles in `ai_recommender/articles.json` and returns matches based on keywords and term frequency.

### SQL example

Load the schema and then the seed data in a compatible SQL environment:

```text
backend/schema.sql
backend/seed_data.sql
```

The repository has not published a cross-database compatibility test, so SQL dialect behavior should be verified for the selected engine.

## Scope and limitations

- Search runs against the small local demo dataset, not a production publication index.
- The recommender is deterministic keyword/term-frequency matching; it is not a trained machine-learning ranking model.
- The repository does not include production ChessLife code, credentials, analytics, or proprietary datasets.
- No automated tests, accessibility audit, load test, or search-quality evaluation is included.
- The demo is intended to illustrate the data flow and interface structure, not to reproduce the scale or operational behavior of a production archive.

## Data flow

```text
sample publication metadata
          ├──> browser search and filtering
          ├──> SQL schema and example queries
          └──> keyword/term-frequency recommendations
```

Keeping the demo self-contained makes it easy to inspect while separating the public example from the original production environment.

