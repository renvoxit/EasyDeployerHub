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

from pydantic import BaseModel


class DeploymentResponse(BaseModel):
    deploy_id: str
    status: str
    created_at: str
