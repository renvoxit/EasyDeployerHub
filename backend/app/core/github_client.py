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
from typing import Any, Dict, List, Tuple

import requests

from app.settings import settings


GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_BASE = "https://api.github.com"

# Maximum per_page allowed by GitHub REST API
_MAX_PER_PAGE = 100


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


def _auth_headers(access_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


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
    resp = requests.post(GITHUB_TOKEN_URL, data=data, headers=headers, timeout=20)
    resp.raise_for_status()
    payload = resp.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"No access_token in GitHub response: {payload}")
    return token


def fetch_user(access_token: str) -> Dict[str, Any]:
    """
    Fetch the authenticated user's profile from GitHub.

    Returns a dict with keys: login, id, name, email, avatar_url, html_url.
    Raises requests.HTTPError on GitHub API errors.
    """
    resp = requests.get(
        f"{GITHUB_API_BASE}/user",
        headers=_auth_headers(access_token),
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "login": data.get("login"),
        "id": data.get("id"),
        "name": data.get("name"),
        "email": data.get("email"),
        "avatar_url": data.get("avatar_url"),
        "html_url": data.get("html_url"),
    }


def fetch_repos(
    access_token: str,
    page: int = 1,
    per_page: int = 30,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Fetch a paginated list of the authenticated user's repositories.

    Returns a tuple of (repo_list, total_count).
    total_count is derived from the Link header when available; otherwise
    it equals the count of items on the current page (last page indicator).

    Each repo dict contains: name, full_name, clone_url, private.
    Raises requests.HTTPError on GitHub API errors.
    """
    per_page = min(per_page, _MAX_PER_PAGE)
    resp = requests.get(
        f"{GITHUB_API_BASE}/user/repos",
        headers=_auth_headers(access_token),
        params={"page": page, "per_page": per_page, "sort": "updated"},
        timeout=20,
    )
    resp.raise_for_status()
    raw = resp.json()

    repos = [
        {
            "name": r.get("name"),
            "full_name": r.get("full_name"),
            "clone_url": r.get("clone_url"),
            "private": r.get("private", False),
        }
        for r in raw
    ]

    # Estimate total: if a "next" link exists we know there are more pages.
    # GitHub doesn't expose a total count directly, so we compute a lower bound.
    link_header = resp.headers.get("Link", "")
    has_next = 'rel="next"' in link_header
    has_last = 'rel="last"' in link_header

    if has_last:
        # Parse last page number from Link header to compute total
        last_page = _parse_last_page(link_header)
        total = (last_page - 1) * per_page + len(repos) if last_page else len(repos)
    elif has_next:
        total = page * per_page + 1  # at least one more page
    else:
        # This is the last (or only) page
        total = (page - 1) * per_page + len(repos)

    return repos, total


def _parse_last_page(link_header: str) -> int | None:
    """Extract the last page number from a GitHub Link header."""
    for part in link_header.split(","):
        part = part.strip()
        if 'rel="last"' in part:
            url_part = part.split(";")[0].strip().strip("<>")
            for param in url_part.split("?")[-1].split("&"):
                if param.startswith("page="):
                    try:
                        return int(param.split("=")[1])
                    except ValueError:
                        return None
    return None
