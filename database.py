import sqlite3
import uuid
from datetime import datetime

DB_NAME = "chat_history.db"


def _get_connection():
    """Internal helper to get a thread-safe SQLite connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn


def init_db():
    """Create the sessions and messages tables if they do not exist."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            )
        """)
        conn.commit()


def create_session(title="New Chat") -> str:
    """Create a new chat session and return its unique ID."""
    session_id = str(uuid.uuid4())
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, datetime.now()),
        )
        conn.commit()
    return session_id


def get_all_sessions():
    """Return all chat sessions sorted by newest first."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM sessions ORDER BY created_at DESC")
        return cursor.fetchall()


def update_session_title(session_id: str, title: str):
    """Update the title of a conversation session."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE sessions SET title = ? WHERE id = ?", (title, session_id))
        conn.commit()


def delete_session(session_id: str):
    """Delete a session and all its messages."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()


def get_session_messages(session_id: str):
    """Fetch all messages for a specific session."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]


def save_message(session_id: str, role: str, content: str):
    """Save a user or assistant message to the database."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now()),
        )
        conn.commit()