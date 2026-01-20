# ROLE:
# GitHub authentication endpoints.
#
# RESPONSIBILITIES:
# - Handle GitHub OAuth flow.
# - Identify user via GitHub.
# - Issue internal auth context.
#
# MUST NOT:
# - Contain GitHub API logic.
# - Store user data directly.
# - Implement security algorithms.

from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from app.core.github_client import build_authorize_url, exchange_code_for_token

router = APIRouter(prefix="/auth/github", tags=["auth"])

# Temporary in-memory storage
_state_store = set()
_token_store = {}  # state -> token


@router.get("/login")
def github_login():
    state = str(uuid4())
    _state_store.add(state)
    url = build_authorize_url(state=state)
    return RedirectResponse(url)


@router.get("/callback")
def github_callback(code: str | None = None, state: str | None = None):
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code/state")

    if state not in _state_store:
        raise HTTPException(status_code=400, detail="Invalid state")

    token = exchange_code_for_token(code)
    _token_store[state] = token

    # Stage 2 dev response: show token + state.
    # Later we’ll store token properly and issue a session.
    return {"ok": True, "state": state, "access_token": token}
