"""Database schema definitions for the Economic Letter Insights application."""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    publication_date TEXT NOT NULL,
    summary TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    letter_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (letter_id) REFERENCES letters(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_letters_date ON letters(publication_date DESC);
CREATE INDEX IF NOT EXISTS idx_questions_letter ON questions(letter_id);
"""


def get_schema() -> str:
    """Return the database schema SQL."""
    return SCHEMA_SQL
