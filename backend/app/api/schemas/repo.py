# ROLE:
# Repository-related API schemas.
#
# RESPONSIBILITIES:
# - Define data structures representing GitHub repositories.
# - Describe repository metadata exposed to clients.
#
# MUST NOT:
# - Contain GitHub API calls.
# - Contain repository selection logic.
# - Contain persistence concerns.

from pydantic import BaseModel, HttpUrl


class RepoSchema(BaseModel):
    """Represents a single GitHub repository returned to the client."""

    name: str
    full_name: str
    clone_url: HttpUrl
    private: bool

    model_config = {"from_attributes": True}


class RepoListResponse(BaseModel):
    """Paginated list of repositories."""

    repos: list[RepoSchema]
    page: int
    per_page: int
    total: int
