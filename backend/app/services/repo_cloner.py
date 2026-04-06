# ROLE:
# Repository cloning service.
#
# RESPONSIBILITIES:
# - Clone selected repositories into temporary workspace.
#
# MUST NOT:
# - Analyze repository contents.
# - Decide deployment strategy.
# - Interact with API layer.

import os
import uuid
import subprocess

from app.core.log_stream import append_log


WORKSPACE_ROOT = "/tmp/edh-workspaces"


def clone_repo(deploy_id: str, repo_url: str) -> str:
    """
    Clone repository into workspace directory.
    """

    workspace_id = str(uuid.uuid4())
    workspace_path = os.path.join(WORKSPACE_ROOT, workspace_id)

    os.makedirs(workspace_path, exist_ok=True)

    append_log(deploy_id, f"Workspace created: {workspace_path}")
    append_log(deploy_id, f"Cloning repo: {repo_url}")

    try:
        subprocess.run(
            ["git", "clone", repo_url, workspace_path],
            check=True,
            capture_output=True,
            text=True,
        )

        append_log(deploy_id, "Repository cloned successfully")

    except subprocess.CalledProcessError as e:
        append_log(deploy_id, "Git clone failed")
        append_log(deploy_id, e.stderr)
        raise

    # Basic validation
    append_log(deploy_id, "Validating repository")

    if not os.path.exists(workspace_path):
        append_log(deploy_id, "Workspace does not exist")
        raise RuntimeError("Workspace not found")

    files = os.listdir(workspace_path)

    if not files:
        append_log(deploy_id, "Repository is empty")
        raise RuntimeError("Repository is empty")

    visible_files = [f for f in files if f != ".git"]

    if not visible_files:
        append_log(deploy_id, "Repository contains only .git")
        raise RuntimeError("Repository contains no project files")

    append_log(deploy_id, "Repository validation passed")

    return workspace_path
