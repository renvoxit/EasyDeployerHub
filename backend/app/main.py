from fastapi import FastAPI
from uuid import uuid4

app = FastAPI(title="Easy Deployer Hub")

deployments = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/deploy")
def deploy():
    deploy_id = str(uuid4())
    deployments[deploy_id] = "pending"
    return {"deploy_id": deploy_id, "status": "pending"}


@app.get("/status/{deploy_id}")
def status(deploy_id: str):
    return {
        "deploy_id": deploy_id,
        "status": deployments.get(deploy_id, "not_found")
    }
