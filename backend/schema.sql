--schema.sql
--example publications database format

--authors
CREATE TABLE IF NOT EXISTS authors (
    author_id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    bio TEXT,
    website VARCHAR(500)
);

--categories
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

--articles
CREATE TABLE IF NOT EXISTS publications (
    publication_id INTEGER PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    author_id INTEGER,
    category_id INTEGER,
    publication_date DATE,
    summary VARCHAR(1000),
    FOREIGN KEY(author_id) REFERENCES authors(author_id),
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
);

--simple full-text index example
CREATE INDEX IF NOT EXISTS idx_publication_date ON publications(publication_date);
CREATE INDEX IF NOT EXISTS idx_category ON publications(category_id);
