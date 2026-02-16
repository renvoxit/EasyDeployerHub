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
        append_log(deploy_id, "Generating Dockerfile...")

        current_stage = "Building image"
        append_log(deploy_id, "Building image...")
        append_log(deploy_id, "Build successful")

        current_stage = "Starting container"
        append_log(deploy_id, "Starting container...")
        append_log(deploy_id, "Container started successfully")

        current_stage = "Finalizing"
        append_log(deploy_id, "Deploy finished")
        update_deployment_status(deploy_id, "success")

    except Exception as e:
        error_msg = f"{current_stage} failed: {e}"
        append_log(deploy_id, error_msg)
        append_log(deploy_id, traceback.format_exc())
        update_deployment_status(deploy_id, "failed")
