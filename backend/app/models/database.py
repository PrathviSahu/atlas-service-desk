"""
SQLite database setup and connection helpers.
"""
import sqlite3
import os


def get_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str) -> None:
    """Create tables if they do not exist."""
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS technicians (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'available'
        );

        CREATE TABLE IF NOT EXISTS requests (
            id                  TEXT PRIMARY KEY,
            customer_id         TEXT NOT NULL,
            channel             TEXT NOT NULL,
            message             TEXT NOT NULL,
            received_at         TEXT NOT NULL,
            priority            TEXT NOT NULL DEFAULT 'normal',
            status              TEXT NOT NULL DEFAULT 'open',
            technician_id       TEXT REFERENCES technicians(id),
            is_duplicate        INTEGER NOT NULL DEFAULT 0,
            duplicate_of        TEXT REFERENCES requests(id),
            needs_clarification INTEGER NOT NULL DEFAULT 0,
            missing_information TEXT,
            notes               TEXT,
            created_at          TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()
