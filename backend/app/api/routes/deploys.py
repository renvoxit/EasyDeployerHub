# ROLE:
# Deployment control endpoints.
#
# RESPONSIBILITIES:
# - Trigger deployment process.
# - Expose deployment status.
#
# MUST NOT:
# - Execute deployment logic.
# - Run Docker commands.
# - Manage queues directly.

import threading
import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas.deploy import (
    DeploymentCreate,
    DeploymentDiagnosticsResponse,
    DeploymentResponse,
    DeploymentStartResponse,
)
from app.core.deploy_orchestrator import run_deploy
from app.core.log_stream import append_log, read_logs
from app.db.crud.deploys import (
    clear_deployment_runtime,
    clear_deployment_failure,
    create_deployment,
    get_deployment,
    list_deployments,
    update_deployment_status,
)
from app.services.cleanup import cleanup_resources
from app.services.docker_engine import restart_container, stop_container
from app.services.resource_auditor import diagnose_deployment

router = APIRouter(prefix="/deploy", tags=["deploy"])


def _get_deployment_or_404(deploy_id: str):
    deployment = get_deployment(deploy_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.get("", response_model=list[DeploymentResponse])
def list_deploys():
    return list_deployments()


@router.get("/{deploy_id}", response_model=DeploymentResponse)
def get_deploy(deploy_id: str):
    return _get_deployment_or_404(deploy_id)


@router.get("/{deploy_id}/diagnostics", response_model=DeploymentDiagnosticsResponse)
def deployment_diagnostics(deploy_id: str):
    deployment = _get_deployment_or_404(deploy_id)
    return diagnose_deployment(deployment)


@router.delete("/{deploy_id}", response_model=DeploymentResponse)
def delete_deploy(deploy_id: str):
    deployment = _get_deployment_or_404(deploy_id)

    cleanup_resources(
        deploy_id,
        container_id=deployment.get("container_id"),
        image_tag=deployment.get("image_tag"),
        workspace_path=deployment.get("workspace_path"),
    )
    clear_deployment_runtime(deploy_id, clear_public_url=True)
    update_deployment_status(deploy_id, "deleted")

    return _get_deployment_or_404(deploy_id)


@router.post("/{deploy_id}/stop", response_model=DeploymentResponse)
def stop_deploy(deploy_id: str):
    deployment = _get_deployment_or_404(deploy_id)
    container_id = deployment.get("container_id")

    if not container_id:
        raise HTTPException(status_code=409, detail="Deployment has no container to stop")

    stop_container(deploy_id, container_id)
    update_deployment_status(deploy_id, "stopped")

    return _get_deployment_or_404(deploy_id)


@router.post("/{deploy_id}/restart", response_model=DeploymentResponse)
def restart_deploy(deploy_id: str):
    deployment = _get_deployment_or_404(deploy_id)
    container_id = deployment.get("container_id")

    if not container_id:
        raise HTTPException(status_code=409, detail="Deployment has no container to restart")

    update_deployment_status(deploy_id, "running")
    restart_container(deploy_id, container_id)
    clear_deployment_failure(deploy_id)
    update_deployment_status(deploy_id, "success")

    return _get_deployment_or_404(deploy_id)


@router.post("", response_model=DeploymentStartResponse)
def deploy(payload: DeploymentCreate):
    deploy_id = str(uuid.uuid4())

    create_deployment(deploy_id, "pending", payload.repo_url)
    append_log(deploy_id, "Deploy request received")

    thread = threading.Thread(
        target=run_deploy,
        args=(deploy_id, payload.repo_url),
        daemon=True,
    )

    thread.start()

    return {
        "deploy_id": deploy_id,
        "status": "started",
    }


@router.get("/status/{deploy_id}")
def status(deploy_id: str):
    return _get_deployment_or_404(deploy_id)


@router.get("/logs/{deploy_id}")
def logs(deploy_id: str):
    return {
        "deploy_id": deploy_id,
        "logs": read_logs(deploy_id),
    }
