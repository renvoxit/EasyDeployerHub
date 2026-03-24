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

from threading import Thread
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.core.deploy_orchestrator import run_deploy
from app.db.crud.deploys import create_deployment, get_deployment

router = APIRouter(prefix="/deploys", tags=["deploys"])


@router.post("/")
def trigger_deploy(repo_url: str):
    """
    Create deployment and start pipeline in background.
    """

    deploy_id = str(uuid4())

    # create deployment record
    create_deployment(deploy_id, "pending")

    # start deployment pipeline in background
    Thread(
        target=run_deploy,
        args=(deploy_id, repo_url),
        daemon=True,
    ).start()

    # return id immediately
    return {"deploy_id": deploy_id}


@router.get("/{deploy_id}")
def read_deploy(deploy_id: str):
    """
    Return deployment status by id.
    """

    deployment = get_deployment(deploy_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment
