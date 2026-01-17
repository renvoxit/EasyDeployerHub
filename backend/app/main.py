from app.db import update_deployment_status
from app.logs import read_logs
import threading
from app.db import create_deployment, get_deployment
from app.logs import append_log
import time
from fastapi import FastAPI
from uuid import uuid4

from app.db import init_db, create_deployment, get_deployment

app = FastAPI(title="Easy Deployer Hub")

# Simulated deployment process


def fake_deploy(deploy_id: str):
    try:
        steps = [
            "Cloning repository...",
            "Analyzing project...",
            "Generating Dockerfile...",
            "Building image...",
            "Starting container...",
        ]

        for step in steps:
            append_log(deploy_id, step)
            time.sleep(1)

        append_log(deploy_id, "Deploy finished")
        update_deployment_status(deploy_id, "success")

    except Exception as e:
        append_log(deploy_id, f"Deploy failed: {e}")
        update_deployment_status(deploy_id, "failed")

# API Endpoints


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
        target=fake_deploy,
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
