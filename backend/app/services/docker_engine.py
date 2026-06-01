# ROLE:
# Docker execution service.
#
# RESPONSIBILITIES:
# - Build Docker images.
# - Run and stop containers.
#
# MUST NOT:
# - Decide deployment flow.
# - Manage proxy configuration.
# - Handle logging policies.

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid

from app.core.log_stream import append_log
from app.services.port_allocator import allocate_port

DOCKER_NETWORK = "edh-network"


def _ensure_network(deploy_id: str):
    process = subprocess.run(
        ["docker", "network", "inspect", DOCKER_NETWORK],
        capture_output=True,
        text=True,
    )

    if process.returncode == 0:
        return

    _run_command(deploy_id, ["docker", "network", "create", DOCKER_NETWORK])


def _run_command(deploy_id: str, command: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    append_log(deploy_id, f"Running command: {' '.join(command)}")

    process = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if process.stdout:
        append_log(deploy_id, process.stdout.strip())

    if process.stderr:
        append_log(deploy_id, process.stderr.strip())

    if process.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {process.returncode}: {' '.join(command)}")

    return process


def _read_exposed_port(workspace_path: str) -> int:
    dockerfile_path = os.path.join(workspace_path, "Dockerfile")

    try:
        with open(dockerfile_path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0].upper() == "EXPOSE":
                    return int(parts[1].split("/")[0])
    except OSError:
        pass

    return 8000


def _image_label(image_tag: str, label: str) -> str:
    process = subprocess.run(
        [
            "docker",
            "image",
            "inspect",
            image_tag,
            "--format",
            f"{{{{ index .Config.Labels \"{label}\" }}}}",
        ],
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        return ""

    return process.stdout.strip()


def _container_label(container_id: str, label: str) -> str:
    process = subprocess.run(
        [
            "docker",
            "inspect",
            container_id,
            "--format",
            f"{{{{ index .Config.Labels \"{label}\" }}}}",
        ],
        capture_output=True,
        text=True,
    )

    if process.returncode != 0:
        return ""

    return process.stdout.strip()


def _wait_for_http(deploy_id: str, url: str, timeout_seconds: float = 20, delay_seconds: float = 0.5):
    append_log(deploy_id, f"Checking HTTP health: {url}")

    last_error = None
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= response.status <= 399:
                    append_log(deploy_id, f"HTTP health check passed: {response.status}")
                    return

                last_error = RuntimeError(f"Unexpected HTTP status: {response.status}")
        except urllib.error.HTTPError as e:
            last_error = RuntimeError(f"Unexpected HTTP status: {e.code}")
        except Exception as e:
            last_error = e

        time.sleep(delay_seconds)

    raise RuntimeError(f"HTTP health check timed out after {timeout_seconds}s: {last_error}")


def build_image(deploy_id: str, workspace_path: str) -> str:
    """
    Build a Docker image from the rendered deployment workspace.
    """

    append_log(deploy_id, "Building Docker image...")

    image_tag = f"easydeployer-{uuid.uuid4().hex[:8]}"
    container_port = _read_exposed_port(workspace_path)

    _run_command(
        deploy_id,
        [
            "docker",
            "build",
            "--label",
            f"easydeployer.deploy_id={deploy_id}",
            "--label",
            f"easydeployer.port={container_port}",
            "-t",
            image_tag,
            ".",
        ],
        cwd=workspace_path,
    )

    append_log(deploy_id, f"Image built successfully: {image_tag}")

    return image_tag


def run_container(deploy_id: str, image_tag: str) -> str:
    """
    Start a Docker container and expose it on a free local host port.
    """

    append_log(deploy_id, f"Starting container from image: {image_tag}")

    container_name = f"easydeployer-{deploy_id[:8]}-{uuid.uuid4().hex[:6]}"
    container_port = int(_image_label(image_tag, "easydeployer.port") or "8000")
    host_port = allocate_port()
    route_path = f"/deployments/{deploy_id[:12]}"
    route_url = f"http://localhost:8080{route_path}/"

    _ensure_network(deploy_id)

    process = _run_command(
        deploy_id,
        [
            "docker",
            "run",
            "-d",
            "--name",
            container_name,
            "--label",
            f"easydeployer.deploy_id={deploy_id}",
            "--label",
            f"easydeployer.host_port={host_port}",
            "--label",
            f"easydeployer.container_port={container_port}",
            "--label",
            f"easydeployer.route_url={route_url}",
            "--label",
            "traefik.enable=true",
            "--label",
            f"traefik.http.routers.{container_name}.rule=Host(`localhost`) && PathPrefix(`{route_path}`)",
            "--label",
            f"traefik.http.routers.{container_name}.entrypoints=web",
            "--label",
            f"traefik.http.routers.{container_name}.middlewares={container_name}-strip",
            "--label",
            f"traefik.http.middlewares.{container_name}-strip.stripprefix.prefixes={route_path}",
            "--label",
            f"traefik.http.services.{container_name}.loadbalancer.server.port={container_port}",
            "--network",
            DOCKER_NETWORK,
            "-p",
            f"127.0.0.1:{host_port}:{container_port}",
            image_tag,
        ],
    )

    container_id = process.stdout.strip()

    inspect = _run_command(
        deploy_id,
        [
            "docker",
            "inspect",
            container_id,
            "--format",
            "{{json .State}}",
        ],
    )

    state = json.loads(inspect.stdout)

    if not state.get("Running"):
        logs = subprocess.run(
            ["docker", "logs", container_id],
            capture_output=True,
            text=True,
        )

        if logs.stdout:
            append_log(deploy_id, logs.stdout.strip())

        if logs.stderr:
            append_log(deploy_id, logs.stderr.strip())

        raise RuntimeError(f"Container exited during startup: {state.get('Error') or state.get('Status')}")

    append_log(deploy_id, f"Container started: {container_id}")
    append_log(deploy_id, f"Container port {container_port} mapped to host port {host_port}")
    append_log(deploy_id, f"Traefik route URL: {route_url}")
    _wait_for_http(deploy_id, f"http://127.0.0.1:{host_port}/")

    return container_id


def stop_container(deploy_id: str, container_id: str):
    append_log(deploy_id, f"Stopping container: {container_id}")
    _run_command(deploy_id, ["docker", "stop", container_id])


def restart_container(deploy_id: str, container_id: str):
    append_log(deploy_id, f"Restarting container: {container_id}")
    _run_command(deploy_id, ["docker", "restart", container_id])

    host_port = _container_label(container_id, "easydeployer.host_port")

    if host_port:
        _wait_for_http(deploy_id, f"http://127.0.0.1:{host_port}/")


def remove_container(deploy_id: str, container_id: str):
    append_log(deploy_id, f"Removing container: {container_id}")
    _run_command(deploy_id, ["docker", "rm", "-f", container_id])


def remove_image(deploy_id: str, image_tag: str):
    append_log(deploy_id, f"Removing image: {image_tag}")
    _run_command(deploy_id, ["docker", "rmi", "-f", image_tag])
