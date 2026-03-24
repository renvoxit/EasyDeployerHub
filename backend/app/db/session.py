# ROLE:
# Database session management.
#
# RESPONSIBILITIES:
# - Create and manage database sessions.
# - Provide session factory for other layers.
#
# MUST NOT:
# - Contain business logic.
# - Execute queries directly.
# - Depend on HTTP or API layers.

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "deployer.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            public_url TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # add public_url column for existing databases
    cur.execute("PRAGMA table_info(deployments)")
    columns = [row[1] for row in cur.fetchall()]
    if "public_url" not in columns:
        cur.execute("ALTER TABLE deployments ADD COLUMN public_url TEXT")

    conn.commit()
    conn.close()
