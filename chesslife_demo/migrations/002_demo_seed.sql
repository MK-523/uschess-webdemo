INSERT INTO authors (author_id, name, bio, website) VALUES
    (1, 'GM Anna', 'Grandmaster and demo columnist.', ''),
    (2, 'IM Ravi', 'International Master and demo columnist.', '');

INSERT INTO categories (category_id, name) VALUES
    (1, 'Openings'),
    (2, 'Endgames'),
    (3, 'Tactics'),
    (4, 'Annotated Games');

INSERT INTO publications (
    publication_id,
    title,
    content,
    author_id,
    category_id,
    publication_date,
    summary
) VALUES
    (
        1,
        'The Sicilian Revisited',
        'Detailed analysis of the modern Sicilian Defense and novelties. Includes move-by-move commentary and typical plans.',
        2,
        1,
        '2024-11-01',
        'A deep dive into modern Sicilian lines.'
    ),
    (
        2,
        'Basic King and Pawn Endgames',
        'A practical guide to king and pawn endgames with illustrative positions and conversion plans.',
        1,
        2,
        '2025-01-10',
        'Foundational endgames for club players.'
    ),
    (
        3,
        'Tactical Patterns You Must Know',
        'Collection of tactical motifs including forks, pins, skewers, and discovered attacks. Multiple puzzles included.',
        2,
        3,
        '2024-08-19',
        'A training set of tactical exercises.'
    ),
    (
        4,
        'World Championship 1993: Game 5',
        'Annotated moves from Game 5 with modern engine evaluation and historical notes.',
        1,
        4,
        '1993-07-22',
        'Historical annotated game with commentary.'
    ),
    (
        5,
        'Practical Middlegame Plans',
        'How to build plans from slightly better positions, pawn structure evaluation, and piece coordination techniques.',
        2,
        1,
        '2025-02-14',
        'Middlegame plans for improving players.'
    );


