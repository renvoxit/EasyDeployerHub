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

from app.core.log_stream import append_log


def analyze_project(deploy_id: str, workspace_path: str) -> str:
    """
    Temporary stub analyzer.
    Real detection logic will be added later.
    """

    append_log(deploy_id, f"Analyzing workspace: {workspace_path}")

    # TEMP: hardcoded project type
    project_type = "python-fastapi"

    append_log(deploy_id, f"Detected project type: {project_type}")

    return project_type
