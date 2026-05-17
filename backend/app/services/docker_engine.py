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
import uuid

from app.core.log_stream import append_log
from app.services.port_allocator import allocate_port


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

    return container_id
