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

from app.core.log_stream import append_log

WORKSPACE_ROOT = "/tmp/easydeployer"


def clone_repo(deploy_id: str, repo_url: str) -> str:
    """
    Creates workspace directory for deployment.
    Real git clone will be added later.
    """

    workspace_id = str(uuid.uuid4())
    workspace_path = os.path.join(WORKSPACE_ROOT, workspace_id)

    os.makedirs(workspace_path, exist_ok=True)

    append_log(deploy_id, f"Workspace created: {workspace_path}")
    append_log(deploy_id, f"Repo placeholder for: {repo_url}")

    return workspace_path
