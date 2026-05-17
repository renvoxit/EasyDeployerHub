# ROLE:
# Project analysis service.
#
# RESPONSIBILITIES:
# - Analyze repository structure.
# - Detect project type, runtime, and ports.
#
# MUST NOT:
# - Generate Dockerfiles.
# - Execute build or run steps.
# - Contain deployment orchestration logic.

import json
import os

from app.core.log_stream import append_log


def _read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().lower()
    except OSError:
        return ""


def _has_file(workspace_path: str, *names: str) -> bool:
    return any(os.path.exists(os.path.join(workspace_path, name)) for name in names)


def _detect_python_project(workspace_path: str) -> str | None:
    requirements = _read_text(os.path.join(workspace_path, "requirements.txt"))
    pyproject = _read_text(os.path.join(workspace_path, "pyproject.toml"))
    app_py = _read_text(os.path.join(workspace_path, "app.py"))
    main_py = _read_text(os.path.join(workspace_path, "main.py"))
    combined = "\n".join([requirements, pyproject, app_py, main_py])

    if "fastapi" in combined:
        return "python-fastapi"

    if "flask" in combined:
        return "python-flask"

    if requirements or pyproject:
        return "python-fastapi"

    return None


def _detect_node_project(workspace_path: str) -> str | None:
    package_path = os.path.join(workspace_path, "package.json")

    if not os.path.exists(package_path):
        return None

    try:
        with open(package_path, encoding="utf-8") as f:
            package = json.load(f)
    except (OSError, json.JSONDecodeError):
        return "node"

    dependencies = {}
    dependencies.update(package.get("dependencies", {}))
    dependencies.update(package.get("devDependencies", {}))

    if any(name in dependencies for name in ("@vitejs/plugin-react", "react", "react-dom")):
        return "react"

    return "node"


def analyze_project(deploy_id: str, workspace_path: str) -> str:
    """
    Detect project type from repository files.
    """

    append_log(deploy_id, f"Analyzing workspace: {workspace_path}")

    if not os.path.isdir(workspace_path):
        raise RuntimeError("Workspace not found")

    project_type = (
        _detect_node_project(workspace_path)
        or _detect_python_project(workspace_path)
    )

    if not project_type and _has_file(workspace_path, "index.html"):
        project_type = "static"

    if not project_type:
        raise RuntimeError("Unsupported project type")

    append_log(deploy_id, f"Detected project type: {project_type}")

    return project_type
