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

import json
import subprocess

from app.core.log_stream import append_log


def expose_service(deploy_id: str, container_id: str) -> str:
    """
    Return the local URL exposed by the Docker port mapping.
    """

    append_log(deploy_id, f"Configuring proxy for container: {container_id}")

    process = subprocess.run(
        [
            "docker",
            "inspect",
            container_id,
            "--format",
            "{{json .NetworkSettings.Ports}}",
        ],
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        if process.stderr:
            append_log(deploy_id, process.stderr.strip())
        raise RuntimeError("Failed to inspect container ports")

    ports = json.loads(process.stdout)
    host_port = None

    for bindings in ports.values():
        if bindings:
            host_port = bindings[0].get("HostPort")
            break

    if not host_port:
        raise RuntimeError("Container has no exposed host port")

    public_url = f"http://127.0.0.1:{host_port}"

    append_log(deploy_id, f"Service exposed at: {public_url}")

    return public_url
