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
from app.db.crud.deploys import (
    clear_deployment_runtime,
    update_deployment_result,
    update_deployment_runtime,
    update_deployment_status,
)
from app.services.repo_cloner import clone_repo
from app.services.analyzer import analyze_project
from app.services.template_renderer import render_templates
from app.services.docker_engine import build_image, run_container
from app.services.proxy_manager import expose_service
from app.services.cleanup import cleanup_resources


def run_deploy(deploy_id: str, repo_url: str):
    """
    Full deployment pipeline
    """
    current_stage = "starting"
    workspace_path = None
    image_tag = None
    container_id = None

    try:
        update_deployment_status(deploy_id, "running")
        append_log(deploy_id, "Deployment started")

        # Clone repo
        current_stage = "cloning repository"
        workspace_path = clone_repo(deploy_id, repo_url)
        update_deployment_runtime(deploy_id, workspace_path=workspace_path)

        # Analyze project
        current_stage = "analyzing project"
        project_type = analyze_project(deploy_id, workspace_path)

        # Render templates
        current_stage = "rendering templates"
        render_templates(deploy_id, workspace_path, project_type)

        # Build image
        current_stage = "building image"
        image_tag = build_image(deploy_id, workspace_path)
        update_deployment_runtime(deploy_id, image_tag=image_tag)

        # Run container
        current_stage = "starting container"
        container_id = run_container(deploy_id, image_tag)
        update_deployment_runtime(deploy_id, container_id=container_id)

        # Expose service
        current_stage = "configuring proxy"
        public_url = expose_service(deploy_id, container_id)

        append_log(deploy_id, f"Deployment finished: {public_url}")

        update_deployment_result(
            deploy_id,
            "success",
            public_url,
        )

        return {
            "deploy_id": deploy_id,
            "public_url": public_url,
            "status": "success",
        }

    except Exception as e:
        append_log(deploy_id, f"Deployment failed during {current_stage}: {e}")
        append_log(deploy_id, traceback.format_exc())
        cleanup_resources(
            deploy_id,
            container_id=container_id,
            image_tag=image_tag,
            workspace_path=workspace_path,
        )
        clear_deployment_runtime(deploy_id, clear_public_url=True)
        update_deployment_status(deploy_id, "failed")
        raise
