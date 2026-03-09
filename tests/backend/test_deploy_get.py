from pathlib import Path
import os
import sqlite3
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("GITHUB_CLIENT_ID", "test-client-id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GITHUB_REDIRECT_URI", "http://localhost/callback")

from app.main import app
from app.db.session import DB_PATH, init_db

client = TestClient(app)


def setup_function():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


def insert_deployment(deploy_id: str, status: str, created_at: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deployments (id, status, created_at) VALUES (?, ?, ?)",
        (deploy_id, status, created_at),
    )
    conn.commit()
    conn.close()


def test_get_deployment_returns_record():
    insert_deployment("dep-123", "running", "2026-02-20T03:25:00")

    response = client.get("/deploy/dep-123")

    assert response.status_code == 200
    assert response.json() == {
        "deploy_id": "dep-123",
        "status": "running",
        "created_at": "2026-02-20T03:25:00",
    }


def test_get_deployment_returns_404_for_missing_id():
    response = client.get("/deploy/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Deployment not found"}
