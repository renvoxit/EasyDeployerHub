from pathlib import Path
import builtins
import io
import os
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services import analyzer


def virtual_workspace(monkeypatch, files: dict[str, str]):
    workspace_path = "C:\\virtual-workspace"
    normalized_files = {
        os.path.normpath(os.path.join(workspace_path, name)): content
        for name, content in files.items()
    }

    def fake_isdir(path):
        return os.path.normpath(path) == os.path.normpath(workspace_path)

    def fake_exists(path):
        return os.path.normpath(path) in normalized_files

    def fake_open(path, encoding=None):
        normalized_path = os.path.normpath(path)
        if normalized_path not in normalized_files:
            raise OSError(path)
        return io.StringIO(normalized_files[normalized_path])

    monkeypatch.setattr(analyzer, "append_log", lambda deploy_id, line: None)
    monkeypatch.setattr(analyzer.os.path, "isdir", fake_isdir)
    monkeypatch.setattr(analyzer.os.path, "exists", fake_exists)
    monkeypatch.setattr(builtins, "open", fake_open)

    return workspace_path


def test_analyze_project_detects_fastapi(monkeypatch):
    workspace_path = virtual_workspace(monkeypatch, {"requirements.txt": "fastapi\nuvicorn\n"})

    project_type = analyzer.analyze_project("deploy-1", workspace_path)

    assert project_type == "python-fastapi"


def test_analyze_project_detects_flask(monkeypatch):
    workspace_path = virtual_workspace(monkeypatch, {"requirements.txt": "flask\n"})

    project_type = analyzer.analyze_project("deploy-1", workspace_path)

    assert project_type == "python-flask"


def test_analyze_project_detects_react(monkeypatch):
    workspace_path = virtual_workspace(
        monkeypatch,
        {
            "package.json": (
                '{"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}'
            )
        },
    )

    project_type = analyzer.analyze_project("deploy-1", workspace_path)

    assert project_type == "react"


def test_analyze_project_detects_node(monkeypatch):
    workspace_path = virtual_workspace(
        monkeypatch,
        {"package.json": '{"scripts": {"start": "node server.js"}}'},
    )

    project_type = analyzer.analyze_project("deploy-1", workspace_path)

    assert project_type == "node"


def test_analyze_project_detects_static(monkeypatch):
    workspace_path = virtual_workspace(monkeypatch, {"index.html": "<h1>Hello</h1>"})

    project_type = analyzer.analyze_project("deploy-1", workspace_path)

    assert project_type == "static"


def test_analyze_project_rejects_unknown_project(monkeypatch):
    workspace_path = virtual_workspace(monkeypatch, {})

    with pytest.raises(RuntimeError, match="Unsupported project type"):
        analyzer.analyze_project("deploy-1", workspace_path)
