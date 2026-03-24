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

from fastapi import FastAPI

from app.db.session import init_db
from app.api.routes.auth_github import router as github_auth_router
from app.api.routes.repos import router as github_repos_router
from app.api.routes.user import router as github_user_router
from app.api.routes.deploys import router as deploys_router

app = FastAPI(title="Easy Deployer Hub")

app.include_router(github_auth_router)
app.include_router(github_repos_router)
app.include_router(github_user_router)
app.include_router(deploys_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
