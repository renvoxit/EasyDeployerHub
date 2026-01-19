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

from app.core.log_stream import append_log
from app.db.crud.deploys import update_deployment_status


def run_deploy(deploy_id: str):
    try:
        steps = [
            "Cloning repository...",
            "Analyzing project...",
            "Generating Dockerfile...",
            "Building image...",
            "Starting container...",
        ]

        for step in steps:
            append_log(deploy_id, step)
            time.sleep(1)

        append_log(deploy_id, "Deploy finished")
        update_deployment_status(deploy_id, "success")

    except Exception as e:
        append_log(deploy_id, f"Deploy failed: {e}")
        update_deployment_status(deploy_id, "failed")
