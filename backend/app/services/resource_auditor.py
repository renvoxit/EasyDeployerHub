# ROLE:
# Deployment resource diagnostics service.
#
# RESPONSIBILITIES:
# - Inspect Docker and filesystem resources for a deployment.
# - Compare persisted deployment state with real runtime state.
# - Report resource inconsistencies.
#
# MUST NOT:
# - Mutate deployment state.
# - Stop, restart, remove, or create resources.
# - Execute deployment lifecycle actions.

import os
import subprocess
import urllib.request


ACTIVE_STATUSES = {"pending", "running", "success", "stopped", "failed"}


def _docker_inspect_exists(resource_type: str, resource_id: str | None) -> bool:
    if not resource_id:
        return False

    try:
        process = subprocess.run(
            ["docker", resource_type, "inspect", resource_id],
            capture_output=True,
            text=True,
        )
    except OSError:
        return False

    return process.returncode == 0


def container_exists(container_id: str | None) -> bool:
    return _docker_inspect_exists("container", container_id)


def image_exists(image_tag: str | None) -> bool:
    return _docker_inspect_exists("image", image_tag)


def container_state(container_id: str | None) -> str | None:
    if not container_id:
        return None

    try:
        process = subprocess.run(
            ["docker", "inspect", container_id, "--format", "{{.State.Status}}"],
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if process.returncode != 0:
        return None

    return process.stdout.strip() or None


def workspace_exists(workspace_path: str | None) -> bool:
    return bool(workspace_path and os.path.exists(workspace_path))


def health_check_status(public_url: str | None) -> str:
    if not public_url:
        return "not_configured"

    try:
        with urllib.request.urlopen(public_url, timeout=3) as response:
            if 200 <= response.status <= 399:
                return "ok"
            return f"failed_http_{response.status}"
    except Exception as e:
        return f"failed: {e}"


def _find_inconsistencies(
    deployment: dict,
    container_exists_value: bool,
    container_state_value: str | None,
    image_exists_value: bool,
    workspace_exists_value: bool,
    health_check_value: str,
) -> list[str]:
    status = deployment.get("status")
    inconsistencies = []

    if status == "success" and not container_exists_value:
        inconsistencies.append("success but container missing")

    if status == "success" and container_exists_value and container_state_value != "running":
        inconsistencies.append("success but container not running")

    if status == "success" and health_check_value != "ok":
        inconsistencies.append("success but health check fails")

    if status == "deleted":
        if container_exists_value:
            inconsistencies.append("deleted but container still exists")
        if image_exists_value:
            inconsistencies.append("deleted but image still exists")
        if workspace_exists_value:
            inconsistencies.append("deleted but workspace still exists")

    if status == "stopped" and container_state_value == "running":
        inconsistencies.append("stopped but container running")

    if status == "failed" and not deployment.get("failure_stage"):
        inconsistencies.append("failed but failure_stage missing")

    if status == "failed" and not deployment.get("failure_reason"):
        inconsistencies.append("failed but failure_reason missing")

    if status in ACTIVE_STATUSES and deployment.get("workspace_path") and not workspace_exists_value:
        inconsistencies.append("active deployment but workspace missing")

    return inconsistencies


def diagnose_deployment(deployment: dict) -> dict:
    container_exists_value = container_exists(deployment.get("container_id"))
    container_state_value = container_state(deployment.get("container_id")) if container_exists_value else None
    image_exists_value = image_exists(deployment.get("image_tag"))
    workspace_exists_value = workspace_exists(deployment.get("workspace_path"))
    health_check_value = health_check_status(deployment.get("public_url"))

    return {
        "deploy_id": deployment["deploy_id"],
        "db_status": deployment["status"],
        "container_exists": container_exists_value,
        "container_state": container_state_value,
        "image_exists": image_exists_value,
        "workspace_exists": workspace_exists_value,
        "public_url": deployment.get("public_url"),
        "health_check_status": health_check_value,
        "inconsistencies": _find_inconsistencies(
            deployment,
            container_exists_value,
            container_state_value,
            image_exists_value,
            workspace_exists_value,
            health_check_value,
        ),
    }
