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
    update_deployment_failure,
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

STAGE_MESSAGES = {
    "clone": "Clone repository",
    "analyze": "Analyze project",
    "render_template": "Render deployment templates",
    "docker_build": "Build Docker image",
    "docker_run": "Run Docker container",
    "health_check": "Check runtime health",
    "proxy": "Configure proxy",
    "cleanup": "Cleanup resources",
    "unknown": "Unknown deployment stage",
}


def _failure_reason(error: Exception) -> str:
    reason = str(error).strip()

    if not reason:
        return error.__class__.__name__

    return reason


def _normalize_failure_stage(current_stage: str, error: Exception) -> str:
    reason = _failure_reason(error).lower()

    if "http health check" in reason:
        return "health_check"

    if current_stage in STAGE_MESSAGES:
        return current_stage

    return "unknown"


def run_deploy(deploy_id: str, repo_url: str):
    """
    Full deployment pipeline
    """
    current_stage = "unknown"
    workspace_path = None
    image_tag = None
    container_id = None

    try:
        update_deployment_status(deploy_id, "running")
        append_log(deploy_id, "Deployment started")

        # Clone repo
        current_stage = "clone"
        append_log(deploy_id, f"Stage started: {current_stage} ({STAGE_MESSAGES[current_stage]})")
        workspace_path = clone_repo(deploy_id, repo_url)
        update_deployment_runtime(deploy_id, workspace_path=workspace_path)

        # Analyze project
        current_stage = "analyze"
        append_log(deploy_id, f"Stage started: {current_stage} ({STAGE_MESSAGES[current_stage]})")
        project_type = analyze_project(deploy_id, workspace_path)

        # Render templates
        current_stage = "render_template"
        append_log(deploy_id, f"Stage started: {current_stage} ({STAGE_MESSAGES[current_stage]})")
        render_templates(deploy_id, workspace_path, project_type)

        # Build image
        current_stage = "docker_build"
        append_log(deploy_id, f"Stage started: {current_stage} ({STAGE_MESSAGES[current_stage]})")
        image_tag = build_image(deploy_id, workspace_path)
        update_deployment_runtime(deploy_id, image_tag=image_tag)

        # Run container
        current_stage = "docker_run"
        append_log(deploy_id, f"Stage started: {current_stage} ({STAGE_MESSAGES[current_stage]})")
        container_id = run_container(deploy_id, image_tag)
        update_deployment_runtime(deploy_id, container_id=container_id)

        # Expose service
        current_stage = "proxy"
        append_log(deploy_id, f"Stage started: {current_stage} ({STAGE_MESSAGES[current_stage]})")
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
        failure_stage = _normalize_failure_stage(current_stage, e)
        failure_reason = _failure_reason(e)

        append_log(deploy_id, f"Deployment failed during {failure_stage}: {failure_reason}")
        append_log(deploy_id, traceback.format_exc())
        update_deployment_failure(deploy_id, failure_stage, failure_reason)

        append_log(deploy_id, f"Stage started: cleanup ({STAGE_MESSAGES['cleanup']})")
        try:
            cleanup_resources(
                deploy_id,
                container_id=container_id,
                image_tag=image_tag,
                workspace_path=workspace_path,
            )
        except Exception as cleanup_error:
            append_log(deploy_id, f"Cleanup failed: {cleanup_error}")
            update_deployment_failure(deploy_id, "cleanup", _failure_reason(cleanup_error))

        clear_deployment_runtime(deploy_id, clear_public_url=True)
        update_deployment_status(deploy_id, "failed")
        raise
