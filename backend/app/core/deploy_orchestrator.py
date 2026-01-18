import time
import traceback

from app.core.log_stream import append_log
from app.db.crud.deploys import update_deployment_status


def run_deploy(deploy_id: str):
    current_stage = "Initializing"
    try:
        append_log(deploy_id, "Deploy started")

        current_stage = "Cloning repository"
        append_log(deploy_id, "Cloning repository...")
        time.sleep(1)

        current_stage = "Analyzing project"
        append_log(deploy_id, "Analyzing project...")
        time.sleep(1)

        current_stage = "Generating Dockerfile"
        append_log(deploy_id, "Generating Dockerfile...")
        time.sleep(1)

        current_stage = "Building image"
        append_log(deploy_id, "Building image...")
        time.sleep(1)
        append_log(deploy_id, "Build successful")

        current_stage = "Starting container"
        append_log(deploy_id, "Starting container...")
        time.sleep(1)
        append_log(deploy_id, "Container started successfully")

        current_stage = "Finalizing"
        append_log(deploy_id, "Deploy finished")
        update_deployment_status(deploy_id, "success")

    except Exception as e:
        error_msg = f"{current_stage} failed: {e}"
        append_log(deploy_id, error_msg)
        append_log(deploy_id, traceback.format_exc())
        update_deployment_status(deploy_id, "failed")
