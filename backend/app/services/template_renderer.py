# ROLE:
# Deployment template rendering service.
#
# RESPONSIBILITIES:
# - Render Dockerfile and runtime templates.
# - Fill templates with analyzed project data.
#
# MUST NOT:
# - Decide which template to use.
# - Perform filesystem cleanup.
# - Execute Docker commands.

import os
from app.core.log_stream import append_log


def render_templates(deploy_id: str, workspace_path: str, project_type: str) -> str:
    """
    Temporary renderer stub.
    Creates a simple Dockerfile in workspace.
    """

    append_log(deploy_id, f"Rendering templates for: {project_type}")

    dockerfile_path = os.path.join(workspace_path, "Dockerfile")

    dockerfile_content = f"""
# Auto-generated Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

CMD ["echo", "App started successfully"]
"""

    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)

    append_log(deploy_id, f"Dockerfile created at: {dockerfile_path}")

    return dockerfile_path
