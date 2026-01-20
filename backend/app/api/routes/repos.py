# ROLE:
# Repository-related endpoints.
#
# RESPONSIBILITIES:
# - List user GitHub repositories.
# - Select repository for deployment.
#
# MUST NOT:
# - Call GitHub API directly.
# - Contain repository analysis logic.
# - Manage deployment process.

from fastapi import APIRouter, HTTPException

from app.core.github_client import fetch_repos
from app.api.routes.auth_github import _token_store  # Stage 2 shortcut only

router = APIRouter(prefix="/github", tags=["github"])


@router.get("/repos")
def list_repos(state: str):
    token = _token_store.get(state)
    if not token:
        raise HTTPException(
            status_code=401, detail="No token for this state. Login first.")
    return {"repos": fetch_repos(token)}
