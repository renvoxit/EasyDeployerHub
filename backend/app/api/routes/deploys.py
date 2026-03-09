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

from fastapi import APIRouter, HTTPException

from app.api.schemas.deploy import DeploymentResponse
from app.db.crud.deploys import get_deployment

router = APIRouter(prefix="/deploy", tags=["deploy"])


@router.get("/{deploy_id}", response_model=DeploymentResponse)
def get_deploy(deploy_id: str):
    """
    Retrieve deployment information by id.
    """
    deployment = get_deployment(deploy_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment
