-- Standalone query examples from the first repository version.

SELECT title, summary, publication_date FROM publications
ORDER BY publication_date DESC
LIMIT 10;

SELECT p.*, a.name AS author_name, c.name AS category_name
FROM publications p
LEFT JOIN authors a ON p.author_id = a.author_id
LEFT JOIN categories c ON p.category_id = c.category_id
WHERE p.publication_id = 2;

SELECT title, summary FROM publications
WHERE title LIKE '%endgame%' OR summary LIKE '%endgame%';

SELECT p.title, p.publication_date FROM publications p
JOIN categories c ON p.category_id = c.category_id
WHERE c.name = 'Openings';

SELECT c.name, COUNT(*) AS total
FROM publications p
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.name;

