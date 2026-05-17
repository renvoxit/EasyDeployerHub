from pathlib import Path
import sys
import tempfile

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services import analyzer


def make_workspace():
    return Path(tempfile.mkdtemp(dir="C:\\tmp"))


def test_analyze_project_detects_fastapi(monkeypatch):
    workspace_path = make_workspace()
    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)
    (workspace_path / "requirements.txt").write_text("fastapi\nuvicorn\n")

    project_type = analyzer.analyze_project("deploy-1", str(workspace_path))

    assert project_type == "python-fastapi"


def test_analyze_project_detects_flask(monkeypatch):
    workspace_path = make_workspace()
    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)
    (workspace_path / "requirements.txt").write_text("flask\n")

    project_type = analyzer.analyze_project("deploy-1", str(workspace_path))

    assert project_type == "python-flask"


def test_analyze_project_detects_react(monkeypatch):
    workspace_path = make_workspace()
    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)
    (workspace_path / "package.json").write_text(
        '{"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}'
    )

    project_type = analyzer.analyze_project("deploy-1", str(workspace_path))

    assert project_type == "react"


def test_analyze_project_detects_node(monkeypatch):
    workspace_path = make_workspace()
    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)
    (workspace_path / "package.json").write_text('{"scripts": {"start": "node server.js"}}')

    project_type = analyzer.analyze_project("deploy-1", str(workspace_path))

    assert project_type == "node"


def test_analyze_project_detects_static(monkeypatch):
    workspace_path = make_workspace()
    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)
    (workspace_path / "index.html").write_text("<h1>Hello</h1>")

    project_type = analyzer.analyze_project("deploy-1", str(workspace_path))

    assert project_type == "static"


def test_analyze_project_rejects_unknown_project(monkeypatch):
    workspace_path = make_workspace()
    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)

    with pytest.raises(RuntimeError, match="Unsupported project type"):
        analyzer.analyze_project("deploy-1", str(workspace_path))
