# ROLE:
# Dependency injection for API layer.
#
# RESPONSIBILITIES:
# - Provide shared dependencies for routes (db session, auth context).
# - Centralize FastAPI dependencies.
#
# MUST NOT:
# - Contain business logic.
# - Perform complex operations.
# - Call external services directly.

from fastapi import Depends, HTTPException, Query

# Import the token store from auth_github as the single source of truth.
# Routes must NOT import _token_store directly — use get_token() instead.
from app.api.routes.auth_github import _token_store


def get_token(state: str = Query(..., description="OAuth state key")) -> str:
    """
    FastAPI dependency that resolves a GitHub access token from the
    in-memory token store using the `state` query parameter.

    Raises 401 if the state is unknown or the token is missing/empty.
    """
    token = _token_store.get(state, "").strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No valid token for this state. Complete the OAuth login first.",
        )
    return token
