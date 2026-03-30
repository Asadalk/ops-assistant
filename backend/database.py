import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "tasks.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                owner TEXT NOT NULL,
                deadline TEXT NOT NULL,
                priority TEXT NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
                status TEXT NOT NULL CHECK (status IN ('todo', 'in_progress', 'done')),
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
