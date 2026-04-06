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
from pydantic import BaseModel, HttpUrl

from app.api.schemas.deploy import DeploymentResponse
from app.core.deploy_orchestrator import run_deploy
from app.core.log_stream import append_log, read_logs
from app.db.crud.deploys import create_deployment, get_deployment


class DeployRequest(BaseModel):
    repo_url: HttpUrl


router = APIRouter(prefix="/deploy", tags=["deploy"])


@router.get("/{deploy_id}", response_model=DeploymentResponse)
def get_deploy(deploy_id: str):
    deployment = get_deployment(deploy_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment


@router.post("")
def deploy(request: DeployRequest):
    repo_url = str(request.repo_url)
    deploy_id = str(uuid.uuid4())

    create_deployment(deploy_id, "pending")
    append_log(deploy_id, "Deploy request received")

    thread = threading.Thread(
        target=run_deploy,
        args=(deploy_id, repo_url),
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
