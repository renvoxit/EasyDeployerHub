from fastapi import FastAPI
from uuid import uuid4

from app.db import init_db, create_deployment, get_deployment

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
    create_deployment(deploy_id, "pending")
    return {"deploy_id": deploy_id, "status": "pending"}


@app.get("/status/{deploy_id}")
def status(deploy_id: str):
    deployment = get_deployment(deploy_id)
    if not deployment:
        return {"error": "not_found"}
    return deployment
