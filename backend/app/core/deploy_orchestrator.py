# ROLE:
# Deployment orchestration logic.
#
# RESPONSIBILITIES:
# - Coordinate deployment steps.
# - Control deployment workflow state.
# - Delegate execution to services and worker.
#
# MUST NOT:
# - Execute Docker commands directly.
# - Perform file system operations.
# - Contain infrastructure-specific code.

import uuid

from app.services.repo_cloner import clone_repo
from app.services.analyzer import analyze_project
from app.services.template_renderer import render_templates
from app.services.docker_engine import build_image, run_container
from app.services.proxy_manager import expose_service
from app.core.log_stream import append_log


def run_deploy(deploy_id: str, repo_url: str):
    """
    Full deployment pipeline
    """

    append_log(deploy_id, "Deployment started")

    # Clone repo
    workspace_path = clone_repo(deploy_id, repo_url)

    # Analyze project
    project_type = analyze_project(deploy_id, workspace_path)

    # Render templates
    render_templates(deploy_id, workspace_path, project_type)

    # Build image
    image_tag = build_image(deploy_id, workspace_path)

    # Run container
    container_id = run_container(deploy_id, image_tag)

    # Expose service
    public_url = expose_service(deploy_id, container_id)

    append_log(deploy_id, f"Deployment finished: {public_url}")

    return {
        "deploy_id": deploy_id,
        "public_url": public_url,
        "status": "success"
    }
