from pathlib import Path
import os
import sqlite3
import sys
import tempfile

from fastapi.testclient import TestClient
import pytest

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
from app.core import deploy_orchestrator
from app.services import docker_engine, resource_auditor

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
    workspace_path: str | None = None,
    image_tag: str | None = None,
    container_id: str | None = None,
    failure_stage: str | None = None,
    failure_reason: str | None = None,
):
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO deployments (
            id,
            status,
            repo_url,
            public_url,
            created_at,
            workspace_path,
            image_tag,
            container_id,
            failure_stage,
            failure_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            deploy_id,
            status,
            repo_url,
            public_url,
            created_at,
            workspace_path,
            image_tag,
            container_id,
            failure_stage,
            failure_reason,
        ),
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
        "workspace_path": None,
        "image_tag": None,
        "container_id": None,
        "failure_stage": None,
        "failure_reason": None,
    }


def test_get_deployment_returns_failure_info():
    insert_deployment(
        "dep-failed",
        "failed",
        "2026-02-20T03:25:00",
        failure_stage="docker_build",
        failure_reason="Docker build failed",
    )

    response = client.get("/deploy/dep-failed")

    assert response.status_code == 200
    assert response.json()["failure_stage"] == "docker_build"
    assert response.json()["failure_reason"] == "Docker build failed"


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


def test_stop_deployment_updates_status(monkeypatch):
    insert_deployment(
        "dep-stop",
        "success",
        "2026-02-20T03:25:00",
        container_id="container-123",
    )
    stopped = []

    monkeypatch.setattr(deploys, "stop_container", lambda deploy_id, container_id: stopped.append(container_id))

    response = client.post("/deploy/dep-stop/stop")

    assert response.status_code == 200
    assert response.json()["status"] == "stopped"
    assert stopped == ["container-123"]


def test_restart_deployment_updates_status(monkeypatch):
    insert_deployment(
        "dep-restart",
        "stopped",
        "2026-02-20T03:25:00",
        container_id="container-123",
    )
    restarted = []

    monkeypatch.setattr(
        deploys,
        "restart_container",
        lambda deploy_id, container_id: restarted.append(container_id),
    )

    response = client.post("/deploy/dep-restart/restart")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert restarted == ["container-123"]


def test_delete_deployment_cleans_resources(monkeypatch):
    insert_deployment(
        "dep-delete",
        "success",
        "2026-02-20T03:25:00",
        public_url="http://localhost:8080/deployments/dep-delete/",
        workspace_path="C:\\workspace",
        image_tag="image-123",
        container_id="container-123",
    )
    cleaned = []

    def fake_cleanup(deploy_id, container_id=None, image_tag=None, workspace_path=None):
        cleaned.append((container_id, image_tag, workspace_path))

    monkeypatch.setattr(deploys, "cleanup_resources", fake_cleanup)

    response = client.delete("/deploy/dep-delete")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert response.json()["public_url"] is None
    assert response.json()["container_id"] is None
    assert cleaned == [("container-123", "image-123", "C:\\workspace")]


def test_deployment_diagnostics_endpoint_returns_audit(monkeypatch):
    insert_deployment(
        "dep-diagnostics",
        "success",
        "2026-02-20T03:25:00",
        public_url="http://localhost:8080/deployments/dep-diagnostics/",
        workspace_path="C:\\workspace",
        image_tag="image-123",
        container_id="container-123",
    )

    monkeypatch.setattr(
        deploys,
        "diagnose_deployment",
        lambda deployment: {
            "deploy_id": deployment["deploy_id"],
            "db_status": deployment["status"],
            "container_exists": True,
            "container_state": "running",
            "image_exists": True,
            "workspace_exists": True,
            "public_url": deployment["public_url"],
            "health_check_status": "ok",
            "inconsistencies": [],
        },
    )

    response = client.get("/deploy/dep-diagnostics/diagnostics")

    assert response.status_code == 200
    assert response.json() == {
        "deploy_id": "dep-diagnostics",
        "db_status": "success",
        "container_exists": True,
        "container_state": "running",
        "image_exists": True,
        "workspace_exists": True,
        "public_url": "http://localhost:8080/deployments/dep-diagnostics/",
        "health_check_status": "ok",
        "inconsistencies": [],
    }


def test_diagnostics_detects_success_missing_container(monkeypatch):
    deployment = {
        "deploy_id": "dep-success-missing-container",
        "status": "success",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": "C:\\workspace",
        "public_url": "http://localhost:8080/deployments/dep/",
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: False)
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: True)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: True)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "ok")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "success but container missing" in diagnostics["inconsistencies"]


def test_diagnostics_detects_success_container_not_running(monkeypatch):
    deployment = {
        "deploy_id": "dep-success-stopped-container",
        "status": "success",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": "C:\\workspace",
        "public_url": "http://localhost:8080/deployments/dep/",
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: True)
    monkeypatch.setattr(resource_auditor, "container_state", lambda container_id: "exited")
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: True)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: True)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "ok")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "success but container not running" in diagnostics["inconsistencies"]


def test_diagnostics_detects_success_health_check_failure(monkeypatch):
    deployment = {
        "deploy_id": "dep-success-health-fail",
        "status": "success",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": "C:\\workspace",
        "public_url": "http://localhost:8080/deployments/dep/",
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: True)
    monkeypatch.setattr(resource_auditor, "container_state", lambda container_id: "running")
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: True)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: True)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "failed: timeout")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "success but health check fails" in diagnostics["inconsistencies"]


def test_diagnostics_detects_deleted_resources_left(monkeypatch):
    deployment = {
        "deploy_id": "dep-deleted-dirty",
        "status": "deleted",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": "C:\\workspace",
        "public_url": None,
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: True)
    monkeypatch.setattr(resource_auditor, "container_state", lambda container_id: "exited")
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: True)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: True)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "not_configured")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "deleted but container still exists" in diagnostics["inconsistencies"]
    assert "deleted but image still exists" in diagnostics["inconsistencies"]
    assert "deleted but workspace still exists" in diagnostics["inconsistencies"]


def test_diagnostics_detects_stopped_container_running(monkeypatch):
    deployment = {
        "deploy_id": "dep-stopped-running",
        "status": "stopped",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": "C:\\workspace",
        "public_url": "http://localhost:8080/deployments/dep/",
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: True)
    monkeypatch.setattr(resource_auditor, "container_state", lambda container_id: "running")
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: True)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: True)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "ok")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "stopped but container running" in diagnostics["inconsistencies"]


def test_diagnostics_detects_failed_missing_failure_info(monkeypatch):
    deployment = {
        "deploy_id": "dep-failed-no-info",
        "status": "failed",
        "container_id": None,
        "image_tag": None,
        "workspace_path": None,
        "public_url": None,
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: False)
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: False)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: False)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "not_configured")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "failed but failure_stage missing" in diagnostics["inconsistencies"]
    assert "failed but failure_reason missing" in diagnostics["inconsistencies"]


def test_diagnostics_detects_active_workspace_missing(monkeypatch):
    deployment = {
        "deploy_id": "dep-active-no-workspace",
        "status": "running",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": "C:\\workspace",
        "public_url": "http://localhost:8080/deployments/dep/",
        "failure_stage": None,
        "failure_reason": None,
    }

    monkeypatch.setattr(resource_auditor, "container_exists", lambda container_id: True)
    monkeypatch.setattr(resource_auditor, "container_state", lambda container_id: "running")
    monkeypatch.setattr(resource_auditor, "image_exists", lambda image_tag: True)
    monkeypatch.setattr(resource_auditor, "workspace_exists", lambda workspace_path: False)
    monkeypatch.setattr(resource_auditor, "health_check_status", lambda public_url: "ok")

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert "active deployment but workspace missing" in diagnostics["inconsistencies"]


def test_diagnostics_does_not_crash_when_docker_is_unavailable(monkeypatch):
    deployment = {
        "deploy_id": "dep-docker-unavailable",
        "status": "success",
        "container_id": "container-123",
        "image_tag": "image-123",
        "workspace_path": None,
        "public_url": None,
        "failure_stage": None,
        "failure_reason": None,
    }

    def docker_unavailable(*args, **kwargs):
        raise OSError("docker unavailable")

    monkeypatch.setattr(resource_auditor.subprocess, "run", docker_unavailable)

    diagnostics = resource_auditor.diagnose_deployment(deployment)

    assert diagnostics["container_exists"] is False
    assert diagnostics["container_state"] is None
    assert diagnostics["image_exists"] is False
    assert "success but container missing" in diagnostics["inconsistencies"]


def test_get_deployment_returns_404_for_missing_id():
    response = client.get("/deploy/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Deployment not found"}


def test_deploy_records_docker_build_failure_and_triggers_cleanup(monkeypatch):
    insert_deployment("dep-build-fail", "pending", "2026-02-20T03:25:00")
    cleaned = []

    monkeypatch.setattr(deploy_orchestrator, "append_log", lambda deploy_id, line: None)
    monkeypatch.setattr(deploy_orchestrator, "clone_repo", lambda deploy_id, repo_url: "C:\\workspace")
    monkeypatch.setattr(deploy_orchestrator, "analyze_project", lambda deploy_id, workspace_path: "static")
    monkeypatch.setattr(deploy_orchestrator, "render_templates", lambda deploy_id, workspace_path, project_type: None)
    monkeypatch.setattr(
        deploy_orchestrator,
        "build_image",
        lambda deploy_id, workspace_path: (_ for _ in ()).throw(RuntimeError("Docker build failed")),
    )
    monkeypatch.setattr(
        deploy_orchestrator,
        "cleanup_resources",
        lambda deploy_id, container_id=None, image_tag=None, workspace_path=None: cleaned.append(
            (container_id, image_tag, workspace_path)
        ),
    )

    try:
        deploy_orchestrator.run_deploy("dep-build-fail", "https://github.com/example/repo.git")
    except RuntimeError:
        pass

    deployment = client.get("/deploy/dep-build-fail").json()
    assert deployment["status"] == "failed"
    assert deployment["failure_stage"] == "docker_build"
    assert deployment["failure_reason"] == "Docker build failed"
    assert cleaned == [(None, None, "C:\\workspace")]


def test_deploy_records_docker_run_failure_and_triggers_cleanup(monkeypatch):
    insert_deployment("dep-run-fail", "pending", "2026-02-20T03:25:00")
    cleaned = []

    monkeypatch.setattr(deploy_orchestrator, "append_log", lambda deploy_id, line: None)
    monkeypatch.setattr(deploy_orchestrator, "clone_repo", lambda deploy_id, repo_url: "C:\\workspace")
    monkeypatch.setattr(deploy_orchestrator, "analyze_project", lambda deploy_id, workspace_path: "static")
    monkeypatch.setattr(deploy_orchestrator, "render_templates", lambda deploy_id, workspace_path, project_type: None)
    monkeypatch.setattr(deploy_orchestrator, "build_image", lambda deploy_id, workspace_path: "image-123")
    monkeypatch.setattr(
        deploy_orchestrator,
        "run_container",
        lambda deploy_id, image_tag: (_ for _ in ()).throw(RuntimeError("Docker run failed")),
    )
    monkeypatch.setattr(
        deploy_orchestrator,
        "cleanup_resources",
        lambda deploy_id, container_id=None, image_tag=None, workspace_path=None: cleaned.append(
            (container_id, image_tag, workspace_path)
        ),
    )

    try:
        deploy_orchestrator.run_deploy("dep-run-fail", "https://github.com/example/repo.git")
    except RuntimeError:
        pass

    deployment = client.get("/deploy/dep-run-fail").json()
    assert deployment["status"] == "failed"
    assert deployment["failure_stage"] == "docker_run"
    assert deployment["failure_reason"] == "Docker run failed"
    assert cleaned == [(None, "image-123", "C:\\workspace")]


def test_deploy_records_health_check_timeout(monkeypatch):
    insert_deployment("dep-health-fail", "pending", "2026-02-20T03:25:00")

    monkeypatch.setattr(deploy_orchestrator, "append_log", lambda deploy_id, line: None)
    monkeypatch.setattr(deploy_orchestrator, "clone_repo", lambda deploy_id, repo_url: "C:\\workspace")
    monkeypatch.setattr(deploy_orchestrator, "analyze_project", lambda deploy_id, workspace_path: "static")
    monkeypatch.setattr(deploy_orchestrator, "render_templates", lambda deploy_id, workspace_path, project_type: None)
    monkeypatch.setattr(deploy_orchestrator, "build_image", lambda deploy_id, workspace_path: "image-123")
    monkeypatch.setattr(
        deploy_orchestrator,
        "run_container",
        lambda deploy_id, image_tag: (_ for _ in ()).throw(
            RuntimeError("HTTP health check timed out after 20s")
        ),
    )
    monkeypatch.setattr(deploy_orchestrator, "cleanup_resources", lambda *args, **kwargs: None)

    try:
        deploy_orchestrator.run_deploy("dep-health-fail", "https://github.com/example/repo.git")
    except RuntimeError:
        pass

    deployment = client.get("/deploy/dep-health-fail").json()
    assert deployment["status"] == "failed"
    assert deployment["failure_stage"] == "health_check"
    assert deployment["failure_reason"] == "HTTP health check timed out after 20s"


def test_http_health_check_times_out_on_non_success_status(monkeypatch):
    class Response:
        status = 500

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(docker_engine, "append_log", lambda deploy_id, line: None)
    monkeypatch.setattr(docker_engine.urllib.request, "urlopen", lambda url, timeout: Response())
    monkeypatch.setattr(docker_engine.time, "sleep", lambda seconds: None)

    with pytest.raises(RuntimeError, match="HTTP health check timed out"):
        docker_engine._wait_for_http("dep-health", "http://127.0.0.1:1234/", timeout_seconds=0.01)
