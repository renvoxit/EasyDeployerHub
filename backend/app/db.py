import sqlite3
from pathlib import Path
from datetime import datetime

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
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_deployment(deploy_id: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deployments (id, status, created_at) VALUES (?, ?, ?)",
        (deploy_id, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_deployment(deploy_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, status, created_at FROM deployments WHERE id = ?",
        (deploy_id,)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {"deploy_id": row[0], "status": row[1], "created_at": row[2]}
    return None


def update_deployment_status(deploy_id: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE deployments SET status = ? WHERE id = ?",
        (status, deploy_id)
    )
    conn.commit()
    conn.close()
