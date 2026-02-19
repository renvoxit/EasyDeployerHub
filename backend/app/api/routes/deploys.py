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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.crud.deploys import create_deployment, get_deployment
from app.core.deploy_orchestrator import run_deploy

router = APIRouter(prefix="/deploys", tags=["deploys"])


class DeployRequest(BaseModel):
    repo_url: HttpUrl


@router.post("/")
def trigger_deploy(request: DeployRequest, db: Session = Depends(get_db)):
    """
    Create deployment and start pipeline.
    """
    repo_url = str(request.repo_url)

    # Validate input
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")

    # 1. create deployment record
    deployment = create_deployment(db=db, repo_url=repo_url)

    deploy_id = deployment.id

    # 2. start deployment pipeline
    run_deploy(deploy_id)

    # 3. return id to client
    return {"deploy_id": deploy_id}


@router.get("/{deploy_id}")
def get_deployment_status(deploy_id: str, db: Session = Depends(get_db)):
    """
    Get deployment status by ID.
    Returns 404 if deployment is not found.
    """
    deployment = get_deployment(deploy_id=deploy_id)

    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment
