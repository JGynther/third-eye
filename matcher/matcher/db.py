import sqlite3

from .paths import DB


def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY,
                card_id TEXT NOT NULL,
                source TEXT NOT NULL,
                session TEXT NOT NULL
            )
            """
        )


def insert_match(card_id: str, source: str, session: str):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            """
            INSERT INTO matches (card_id, source, session)
            VALUES (?, ?, ?)
            """,
            (card_id, source, session),
        )


def get_session(session_id: str):
    with sqlite3.connect(DB) as conn:
        cursor = conn.execute(
            """
            SELECT * FROM matches WHERE session = ?
            """,
            (session_id,),
        )

        return cursor.fetchall()


def list_sessions():
    with sqlite3.connect(DB) as conn:
        cursor = conn.execute(
            """
            SELECT session
            FROM matches
            GROUP BY session
            ORDER BY MAX(id) DESC;
            """
        )

        return cursor.fetchall()

def list_collection():
    with sqlite3.connect(DB) as conn:
        cursor = conn.execute(
            """
            SELECT card_id
            FROM matches
            GROUP BY card_id
            ORDER BY MAX(id) DESC;
            """
        )

        return cursor.fetchall()
