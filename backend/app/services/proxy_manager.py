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


def _docker_inspect_json(args: list[str]) -> tuple[int, dict | None, str]:
    process = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        return process.returncode, None, process.stderr.strip()

    return process.returncode, json.loads(process.stdout), ""


def _proxy_is_running() -> bool:
    code, state, _ = _docker_inspect_json(
        [
            "docker",
            "inspect",
            "edh-proxy",
            "--format",
            "{{json .State}}",
        ]
    )

    return code == 0 and bool(state and state.get("Running"))


def _direct_local_url(container_id: str) -> str | None:
    code, ports, _ = _docker_inspect_json(
        [
            "docker",
            "inspect",
            container_id,
            "--format",
            "{{json .NetworkSettings.Ports}}",
        ]
    )

    if code != 0 or not ports:
        return None

    for bindings in ports.values():
        if bindings:
            host_port = bindings[0].get("HostPort")
            if host_port:
                return f"http://127.0.0.1:{host_port}"

    return None


def expose_service(deploy_id: str, container_id: str) -> str:
    """
    Return the Traefik URL for the deployed container when proxy is running.
    """

    append_log(deploy_id, f"Configuring proxy for container: {container_id}")

    code, labels, error = _docker_inspect_json(
        [
            "docker",
            "inspect",
            container_id,
            "--format",
            "{{json .Config.Labels}}",
        ],
    )

    if code != 0:
        if error:
            append_log(deploy_id, error)
        raise RuntimeError("Failed to inspect container labels")

    route_url = (labels or {}).get("easydeployer.route_url")

    if route_url and _proxy_is_running():
        append_log(deploy_id, f"Service exposed through Traefik at: {route_url}")
        return route_url

    direct_url = _direct_local_url(container_id)

    if not direct_url:
        raise RuntimeError("Container has no exposed host port")

    append_log(deploy_id, "Traefik proxy is not running; using direct local Docker port")
    append_log(deploy_id, f"Service exposed at: {direct_url}")

    return direct_url
