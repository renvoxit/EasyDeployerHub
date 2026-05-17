# ROLE:
# Deployment-related API schemas.
#
# RESPONSIBILITIES:
# - Define request/response models for deployment operations.
# - Describe deployment status and metadata.
#
# MUST NOT:
# - Contain deployment execution logic.
# - Contain Docker or infrastructure details.
# - Contain state mutation logic.

from pydantic import BaseModel, Field


class DeploymentCreate(BaseModel):
    repo_url: str = Field(..., min_length=1)


class DeploymentStartResponse(BaseModel):
    deploy_id: str
    status: str


class DeploymentResponse(BaseModel):
    deploy_id: str
    status: str
    repo_url: str | None = None
    public_url: str | None = None
    created_at: str
