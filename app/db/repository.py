"""Database repository for managing letters and questions."""

import sqlite3
import logging
from typing import List, Optional, Tuple
from datetime import datetime

from app.db.database import get_connection

logger = logging.getLogger(__name__)


class DatabaseRepository:
    """Repository for database operations on letters and questions."""
    
    def __init__(self, db_path: str):
        """
        Initialize the repository.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
    
    # Letter operations
    
    def get_letters(self, limit: int = 20, offset: int = 0) -> Tuple[List[dict], int]:
        """
        Get paginated list of letters.
        
        Args:
            limit: Maximum number of letters to return
            offset: Number of letters to skip
            
        Returns:
            Tuple of (list of letter dicts, total count)
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM letters")
            total = cursor.fetchone()[0]
            
            # Get paginated letters
            cursor.execute("""
                SELECT id, title, url, publication_date, summary, content, created_at
                FROM letters
                ORDER BY publication_date DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            letters = []
            for row in cursor.fetchall():
                letters.append({
                    'id': row['id'],
                    'title': row['title'],
                    'url': row['url'],
                    'publication_date': row['publication_date'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'created_at': row['created_at']
                })
            
            conn.close()
            return letters, total
        except Exception as e:
            logger.error(f"Error getting letters: {e}")
            raise
    
    def get_letter_by_id(self, letter_id: int) -> Optional[dict]:
        """
        Get a letter by its ID.
        
        Args:
            letter_id: The letter ID
            
        Returns:
            Letter dict or None if not found
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, url, publication_date, summary, content, created_at
                FROM letters
                WHERE id = ?
            """, (letter_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row['id'],
                    'title': row['title'],
                    'url': row['url'],
                    'publication_date': row['publication_date'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'created_at': row['created_at']
                }
            return None
        except Exception as e:
            logger.error(f"Error getting letter by ID {letter_id}: {e}")
            raise
    
    def get_letter_by_url(self, url: str) -> Optional[dict]:
        """
        Get a letter by its URL.
        
        Args:
            url: The letter URL
            
        Returns:
            Letter dict or None if not found
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, url, publication_date, summary, content, created_at
                FROM letters
                WHERE url = ?
            """, (url,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row['id'],
                    'title': row['title'],
                    'url': row['url'],
                    'publication_date': row['publication_date'],
                    'summary': row['summary'],
                    'content': row['content'],
                    'created_at': row['created_at']
                }
            return None
        except Exception as e:
            logger.error(f"Error getting letter by URL {url}: {e}")
            raise
    
    def insert_letter(self, title: str, url: str, publication_date: str, 
                     summary: Optional[str], content: str) -> int:
        """
        Insert a new letter into the database.
        
        Args:
            title: Letter title
            url: Letter URL
            publication_date: Publication date
            summary: Letter summary (optional)
            content: Letter content
            
        Returns:
            ID of the inserted letter
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO letters (title, url, publication_date, summary, content)
                VALUES (?, ?, ?, ?, ?)
            """, (title, url, publication_date, summary, content))
            
            letter_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Inserted letter with ID {letter_id}: {title}")
            return letter_id
        except sqlite3.IntegrityError as e:
            logger.warning(f"Letter already exists with URL {url}")
            raise
        except Exception as e:
            logger.error(f"Error inserting letter: {e}")
            raise
    
    def letter_exists(self, url: str) -> bool:
        """
        Check if a letter with the given URL already exists.
        
        Args:
            url: The letter URL
            
        Returns:
            True if letter exists, False otherwise
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM letters WHERE url = ?", (url,))
            exists = cursor.fetchone() is not None
            
            conn.close()
            return exists
        except Exception as e:
            logger.error(f"Error checking if letter exists: {e}")
            raise
    
    # Question operations
    
    def get_questions_for_letter(self, letter_id: int) -> List[dict]:
        """
        Get all questions for a specific letter.
        
        Args:
            letter_id: The letter ID
            
        Returns:
            List of question dicts ordered by creation time
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, letter_id, question, answer, created_at
                FROM questions
                WHERE letter_id = ?
                ORDER BY created_at ASC
            """, (letter_id,))
            
            questions = []
            for row in cursor.fetchall():
                questions.append({
                    'id': row['id'],
                    'letter_id': row['letter_id'],
                    'question': row['question'],
                    'answer': row['answer'],
                    'created_at': row['created_at']
                })
            
            conn.close()
            return questions
        except Exception as e:
            logger.error(f"Error getting questions for letter {letter_id}: {e}")
            raise
    
    def insert_question(self, letter_id: int, question: str, answer: str) -> int:
        """
        Insert a new question-answer pair.
        
        Args:
            letter_id: The letter ID
            question: The question text
            answer: The answer text
            
        Returns:
            ID of the inserted question
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO questions (letter_id, question, answer)
                VALUES (?, ?, ?)
            """, (letter_id, question, answer))
            
            question_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Inserted question with ID {question_id} for letter {letter_id}")
            return question_id
        except Exception as e:
            logger.error(f"Error inserting question: {e}")
            raise
    
    def delete_question(self, question_id: int) -> bool:
        """
        Delete a question-answer pair.
        
        Args:
            question_id: The question ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            conn = get_connection(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info(f"Deleted question with ID {question_id}")
            else:
                logger.warning(f"Question with ID {question_id} not found")
            
            return deleted
        except Exception as e:
            logger.error(f"Error deleting question: {e}")
            raise
