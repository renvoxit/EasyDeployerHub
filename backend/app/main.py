# ROLE:
# Backend application entry point.
#
# RESPONSIBILITIES:
# - Create FastAPI application instance.
# - Register API routers.
# - Register middleware.
# - Define startup and shutdown lifecycle.
#
# MUST NOT:
# - Contain business logic.
# - Access database directly.
# - Call GitHub, Docker, or deployment logic.

from uuid import uuid4
import threading

from fastapi import FastAPI

from app.core.deploy_orchestrator import run_deploy
from app.core.log_stream import read_logs
from app.db.crud.deploys import create_deployment, get_deployment
from app.db.session import init_db

app = FastAPI(title="Easy Deployer Hub")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/deploy")
def deploy():
    deploy_id = str(uuid4())
    create_deployment(deploy_id, "running")

    thread = threading.Thread(
        target=run_deploy,
        args=(deploy_id,),
        daemon=True
    )
    thread.start()

    return {"deploy_id": deploy_id, "status": "running"}


@app.get("/status/{deploy_id}")
def status(deploy_id: str):
    deployment = get_deployment(deploy_id)
    if not deployment:
        return {"error": "not_found"}
    return deployment


@app.get("/logs/{deploy_id}")
def logs(deploy_id: str):
    return {"logs": read_logs(deploy_id)}
