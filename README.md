# uschess-webdemo

demo/portfolio repository that reproduces a scaled-down version of some aspects of the ChessLife web interface and architecture I worked on.

- Example SQL schema + seed data modelling
- Frontend demo (HTML/JS/CSS) that lists/searches publications.
- Simple Python-based recommender engine (keyword + TF matching) using `ai_recommender/articles.json`.

how do you run:
1. Frontend: open `frontend/index.html` in your browser (it uses a local JSON file).
2. Python Recommender:
   - `cd ai_recommender`
   - `python3 recommender.py "I want endgame practice"`
   - Requires Python 3.8+ (no external libs).
3. SQL:
   - Run `backend/schema.sql` then `backend/seed_data.sql` in your favorite SQL engine (sqlite, mysql, postgres).

- `backend/` : schema and seed queries
- `ai_recommender/` : simple recommender + sample articles (JSON)
- `frontend/` : static demo site (HTML/CSS/JS)


