"""Database initialization and connection management."""

import sqlite3
import logging
from pathlib import Path
from typing import Optional

from app.db.schema import get_schema

logger = logging.getLogger(__name__)


def initialize_database(db_path: str) -> None:
    """
    Initialize the database by creating tables and indexes if they don't exist.
    
    Args:
        db_path: Path to the SQLite database file
    """
    # Ensure the directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Execute schema
        cursor.executescript(get_schema())
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized successfully at {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Get a database connection with foreign keys enabled.
    
    Args:
        db_path: Path to the SQLite database file
        
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
