# ROLE:
# User profile endpoints.
#
# RESPONSIBILITIES:
# - Expose authenticated GitHub user profile.
#
# MUST NOT:
# - Call GitHub API directly.
# - Handle OAuth flow.
# - Store user data.

import logging

from fastapi import APIRouter, Depends, HTTPException
import requests

from app.api.deps import get_token
from app.api.schemas.user import GitHubUser
from app.core.github_client import fetch_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])


@router.get(
    "/me",
    response_model=GitHubUser,
    summary="Get authenticated GitHub user profile",
)
def get_me(token: str = Depends(get_token)) -> GitHubUser:
    """
    Returns the GitHub profile of the currently authenticated user.

    Requires a valid `state` query parameter obtained after completing OAuth.
    """
    try:
        data = fetch_user(token)
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        if status == 401:
            raise HTTPException(status_code=401, detail="GitHub token is invalid or expired.")
        logger.error("GitHub API error fetching user: %s", exc)
        raise HTTPException(status_code=502, detail="GitHub API error. Please try again.")
    except Exception as exc:
        logger.error("Unexpected error fetching user profile: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error.")

    return GitHubUser(**data)
