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

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.crud.deploys import create_deployment
from app.core.deploy_orchestrator import run_deploy

router = APIRouter(prefix="/deploys", tags=["deploys"])


@router.post("/")
def trigger_deploy(repo_url: str, db: Session = Depends(get_db)):
    """
    Create deployment and start pipeline.
    """

    # 1. create deployment record
    deployment = create_deployment(db=db, repo_url=repo_url)

    deploy_id = deployment.id

    # 2. start deployment pipeline
    run_deploy(deploy_id)

    # 3. return id to client
    return {"deploy_id": deploy_id}
