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

import traceback

from app.core.log_stream import append_log
from app.db.crud.deploys import update_deployment_status, update_deployment_result
from app.services.repo_cloner import clone_repo
from app.services.analyzer import analyze_project
from app.services.template_renderer import render_templates
from app.services.docker_engine import build_image, run_container
from app.services.proxy_manager import expose_service


def run_deploy(deploy_id: str, repo_url: str):
    current_stage = "Initializing"
    try:
        update_deployment_status(deploy_id, "running")
        append_log(deploy_id, "Deploy started")

        current_stage = "Cloning repository"
        workspace = clone_repo(deploy_id, repo_url)
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

        current_stage = "Configuring proxy"
        public_url = expose_service(deploy_id, container_id)
        append_log(deploy_id, f"Public URL: {public_url}")

        current_stage = "Finalizing"
        append_log(deploy_id, "Deploy finished")
        update_deployment_result(deploy_id, "success", public_url)

    except Exception as e:
        error_msg = f"{current_stage} failed: {e}"
        append_log(deploy_id, error_msg)
        append_log(deploy_id, traceback.format_exc())
        update_deployment_status(deploy_id, "failed")
