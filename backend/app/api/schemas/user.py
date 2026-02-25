# ROLE:
# User-related API schemas.
#
# RESPONSIBILITIES:
# - Define request/response models representing users.
# - Describe authenticated user identity exposed via API.
#
# MUST NOT:
# - Contain authentication logic.
# - Contain database models.
# - Contain methods with side effects.

from pydantic import BaseModel, HttpUrl


class GitHubUser(BaseModel):
    """Authenticated GitHub user profile returned by GET /github/me."""

    login: str
    id: int
    name: str | None = None
    email: str | None = None
    avatar_url: HttpUrl | None = None
    html_url: HttpUrl

    model_config = {"from_attributes": True}
