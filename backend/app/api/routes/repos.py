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

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
import requests

from app.api.deps import get_token
from app.api.schemas.repo import RepoListResponse, RepoSchema
from app.core.github_client import fetch_repos

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])


@router.get(
    "/repos",
    response_model=RepoListResponse,
    summary="List authenticated user's GitHub repositories",
)
def list_repos(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(30, ge=1, le=100, description="Items per page"),
    token: str = Depends(get_token),
) -> RepoListResponse:
    """
    Returns a paginated list of GitHub repositories for the authenticated user.

    Requires a valid `state` query parameter obtained after completing OAuth.
    """
    try:
        raw_repos, total = fetch_repos(token, page=page, per_page=per_page)
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        if status == 401:
            raise HTTPException(status_code=401, detail="GitHub token is invalid or expired.")
        logger.error("GitHub API error fetching repos: %s", exc)
        raise HTTPException(status_code=502, detail="GitHub API error. Please try again.")
    except Exception as exc:
        logger.error("Unexpected error fetching repos: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.")

    repos = [RepoSchema(**r) for r in raw_repos]
    return RepoListResponse(repos=repos, page=page, per_page=per_page, total=total)
