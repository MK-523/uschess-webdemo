.PHONY: check clean-db dev init-db recommend test

dev:
	python -m chesslife_demo --db instance/chesslife.sqlite3 serve

init-db:
	python -m chesslife_demo --db instance/chesslife.sqlite3 init-db

recommend:
	python -m chesslife_demo --db instance/chesslife.sqlite3 recommend "endgame practice"

test:
	python -m unittest discover -s tests -v

check:
	python -m compileall -q chesslife_demo tests
	python -m unittest discover -s tests -v

clean-db:
	python -c "from pathlib import Path; Path('instance/chesslife.sqlite3').unlink(missing_ok=True)"
