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

import time
import traceback

from app.core.log_stream import append_log
from app.db.crud.deploys import update_deployment_status
from app.services.repo_cloner import clone_repo
from app.services.analyzer import analyze_project
from app.services.template_renderer import render_templates
from app.services.docker_engine import build_image, run_container


def run_deploy(deploy_id: str):
    current_stage = "Initializing"
    try:
        append_log(deploy_id, "Deploy started")

        current_stage = "Cloning repository"
        workspace = clone_repo(deploy_id, "placeholder_repo")
        append_log(deploy_id, f"Workspace path: {workspace}")

        current_stage = "Analyzing project"
        project_type = analyze_project(deploy_id, workspace)
        append_log(deploy_id, f"Project type selected: {project_type}")

        current_stage = "Generating Dockerfile"
        dockerfile_path = render_templates(deploy_id, workspace, project_type)
        append_log(deploy_id, f"Template generated: {dockerfile_path}")

        current_stage = "Building image"
        image_tag = build_image(deploy_id, workspace)

        current_stage = "Starting container"
        container_id = run_container(deploy_id, image_tag)
        append_log(deploy_id, f"Container ID: {container_id}")

        current_stage = "Finalizing"
        append_log(deploy_id, "Deploy finished")
        update_deployment_status(deploy_id, "success")

    except Exception as e:
        error_msg = f"{current_stage} failed: {e}"
        append_log(deploy_id, error_msg)
        append_log(deploy_id, traceback.format_exc())
        update_deployment_status(deploy_id, "failed")
