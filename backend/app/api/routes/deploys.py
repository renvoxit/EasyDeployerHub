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
    DeploymentResponse,
    DeploymentStartResponse,
)
from app.core.deploy_orchestrator import run_deploy
from app.core.log_stream import append_log, read_logs
from app.db.crud.deploys import create_deployment, get_deployment, list_deployments

router = APIRouter(prefix="/deploy", tags=["deploy"])


@router.get("", response_model=list[DeploymentResponse])
def list_deploys():
    return list_deployments()


@router.get("/{deploy_id}", response_model=DeploymentResponse)
def get_deploy(deploy_id: str):
    deployment = get_deployment(deploy_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


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
    deployment = get_deployment(deploy_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.get("/logs/{deploy_id}")
def logs(deploy_id: str):
    return {
        "deploy_id": deploy_id,
        "logs": read_logs(deploy_id),
    }
