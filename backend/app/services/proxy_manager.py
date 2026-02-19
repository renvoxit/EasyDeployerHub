# ROLE:
# Reverse proxy management service.
#
# RESPONSIBILITIES:
# - Configure routing for deployed services.
#
# MUST NOT:
# - Control container lifecycle.
# - Allocate ports.
# - Contain business logic.

import uuid
from app.core.log_stream import append_log


def expose_service(deploy_id: str, container_id: str) -> str:
    """
    Temporary stub for reverse proxy routing.
    Real Traefik/Nginx integration will be added later.
    """

    append_log(deploy_id, f"Configuring proxy for container: {container_id}")

    # TEMP: fake public URL
    subdomain = uuid.uuid4().hex[:6]
    public_url = f"https://{subdomain}.easydeployer.local"

    append_log(deploy_id, f"Service exposed at: {public_url}")

    return public_url
