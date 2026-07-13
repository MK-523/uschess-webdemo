CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    bio TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT ''
) STRICT;

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
) STRICT;

CREATE TABLE publications (
    publication_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES authors(author_id),
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    publication_date TEXT NOT NULL CHECK (
        publication_date = strftime('%Y-%m-%d', publication_date)
    ),
    summary TEXT NOT NULL
) STRICT;

CREATE INDEX idx_publications_date
    ON publications(publication_date DESC);
CREATE INDEX idx_publications_category
    ON publications(category_id, publication_date DESC);

CREATE VIRTUAL TABLE publications_fts USING fts5(
    title,
    summary,
    content,
    content='publications',
    content_rowid='publication_id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER publications_after_insert AFTER INSERT ON publications BEGIN
    INSERT INTO publications_fts(rowid, title, summary, content)
    VALUES (new.publication_id, new.title, new.summary, new.content);
END;

CREATE TRIGGER publications_after_delete AFTER DELETE ON publications BEGIN
    INSERT INTO publications_fts(publications_fts, rowid, title, summary, content)
    VALUES ('delete', old.publication_id, old.title, old.summary, old.content);
END;

CREATE TRIGGER publications_after_update AFTER UPDATE ON publications BEGIN
    INSERT INTO publications_fts(publications_fts, rowid, title, summary, content)
    VALUES ('delete', old.publication_id, old.title, old.summary, old.content);
    INSERT INTO publications_fts(rowid, title, summary, content)
    VALUES (new.publication_id, new.title, new.summary, new.content);
END;


