from pathlib import Path
import os
import sqlite3
import sys
import tempfile

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("GITHUB_CLIENT_ID", "test-client-id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("GITHUB_REDIRECT_URI", "http://localhost/callback")

from app.main import app
from app.db import session as db_session
from app.api.routes import deploys

client = TestClient(app)
TEST_DB_PATH = Path(tempfile.gettempdir()) / "easydeployerhub-test.db"


def setup_function():
    db_session.DB_PATH = TEST_DB_PATH
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db_session.init_db()


def insert_deployment(
    deploy_id: str,
    status: str,
    created_at: str,
    repo_url: str = "https://github.com/example/repo.git",
    public_url: str | None = None,
):
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO deployments (id, status, repo_url, public_url, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (deploy_id, status, repo_url, public_url, created_at),
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
        "repo_url": "https://github.com/example/repo.git",
        "public_url": None,
        "created_at": "2026-02-20T03:25:00",
    }


def test_list_deployments_returns_records_newest_first():
    insert_deployment("dep-old", "success", "2026-02-20T03:25:00")
    insert_deployment("dep-new", "pending", "2026-02-21T03:25:00")

    response = client.get("/deploy")

    assert response.status_code == 200
    assert [item["deploy_id"] for item in response.json()] == ["dep-new", "dep-old"]


def test_create_deployment_accepts_request_body(monkeypatch):
    class ImmediateThread:
        def __init__(self, target, args, daemon):
            self.target = target
            self.args = args
            self.daemon = daemon

        def start(self):
            self.target(*self.args)

    def fake_run_deploy(deploy_id: str, repo_url: str):
        return None

    monkeypatch.setattr(deploys.threading, "Thread", ImmediateThread)
    monkeypatch.setattr(deploys, "run_deploy", fake_run_deploy)
    monkeypatch.setattr(deploys, "append_log", lambda deploy_id, line: None)

    response = client.post(
        "/deploy",
        json={"repo_url": "https://github.com/example/repo.git"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "started"

    deployment = client.get(f"/deploy/{body['deploy_id']}")
    assert deployment.status_code == 200
    assert deployment.json()["repo_url"] == "https://github.com/example/repo.git"


def test_get_deployment_returns_404_for_missing_id():
    response = client.get("/deploy/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Deployment not found"}
