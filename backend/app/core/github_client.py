# ROLE:
# GitHub API interaction layer.
#
# RESPONSIBILITIES:
# - Communicate with GitHub API.
# - Fetch repositories and metadata.
# - Abstract GitHub-specific details.
#
# MUST NOT:
# - Contain business logic.
# - Handle authentication flow directly.
# - Be aware of HTTP layer.

import os
from typing import Any, Dict, List
import requests
from app.settings import settings


GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_BASE = "https://api.github.com"


def _client_id() -> str:
    v = settings.GITHUB_CLIENT_ID
    if not v:
        raise RuntimeError("GITHUB_CLIENT_ID is not set")
    return v


def _client_secret() -> str:
    v = os.getenv("GITHUB_CLIENT_SECRET", "").strip()
    if not v:
        raise RuntimeError("GITHUB_CLIENT_SECRET is not set")
    return v


def _redirect_uri() -> str:
    v = os.getenv("GITHUB_REDIRECT_URI", "").strip()
    if not v:
        raise RuntimeError("GITHUB_REDIRECT_URI is not set")
    return v


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": _client_id(),
        "redirect_uri": _redirect_uri(),
        "scope": "read:user repo",
        "state": state,
    }
    r = requests.Request("GET", GITHUB_AUTH_URL, params=params).prepare()
    return str(r.url)


def exchange_code_for_token(code: str) -> str:
    headers = {"Accept": "application/json"}
    data = {
        "client_id": _client_id(),
        "client_secret": _client_secret(),
        "code": code,
        "redirect_uri": _redirect_uri(),
    }
    resp = requests.post(GITHUB_TOKEN_URL, data=data,
                         headers=headers, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"No access_token in GitHub response: {payload}")
    return token


def fetch_repos(access_token: str) -> List[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(f"{GITHUB_API_BASE}/user/repos",
                        headers=headers, timeout=20)
    resp.raise_for_status()
    repos = resp.json()
    return [
        {
            "name": r.get("name"),
            "full_name": r.get("full_name"),
            "clone_url": r.get("clone_url"),
            "private": r.get("private"),
        }
        for r in repos
    ]
