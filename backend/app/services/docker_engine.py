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

import uuid
from app.core.log_stream import append_log


def build_image(deploy_id: str, workspace_path: str) -> str:
    """
    Temporary stub for Docker image build.
    Real docker build will be added later.
    """

    append_log(deploy_id, "Building Docker image...")

    image_tag = f"easydeployer-{uuid.uuid4().hex[:8]}"

    append_log(deploy_id, f"Image built successfully: {image_tag}")

    return image_tag


def run_container(deploy_id: str, image_tag: str) -> str:
    """
    Temporary stub for container start.
    """

    append_log(deploy_id, f"Starting container from image: {image_tag}")

    container_id = f"container-{uuid.uuid4().hex[:8]}"

    append_log(deploy_id, f"Container started: {container_id}")

    return container_id
