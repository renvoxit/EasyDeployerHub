# ROLE:
# Resource cleanup service.
#
# RESPONSIBILITIES:
# - Remove temporary files and resources.
# - Cleanup containers and artifacts after deployment.
#
# MUST NOT:
# - Decide when cleanup is triggered.
# - Affect active deployments.
# - Contain deployment logic.

import shutil

from app.core.log_stream import append_log
from app.services.docker_engine import remove_container, remove_image


def cleanup_resources(
    deploy_id: str,
    container_id: str | None = None,
    image_tag: str | None = None,
    workspace_path: str | None = None,
):
    """
    Best-effort cleanup for deployment runtime resources.
    """

    if container_id:
        try:
            remove_container(deploy_id, container_id)
            append_log(deploy_id, f"Cleanup result: container removed ({container_id})")
        except Exception as e:
            append_log(deploy_id, f"Cleanup result: container remove failed ({container_id}): {e}")

    if image_tag:
        try:
            remove_image(deploy_id, image_tag)
            append_log(deploy_id, f"Cleanup result: image removed ({image_tag})")
        except Exception as e:
            append_log(deploy_id, f"Cleanup result: image remove failed ({image_tag}): {e}")

    if workspace_path:
        try:
            shutil.rmtree(workspace_path, ignore_errors=True)
            append_log(deploy_id, f"Cleanup result: workspace removed ({workspace_path})")
        except Exception as e:
            append_log(deploy_id, f"Cleanup result: workspace remove failed ({workspace_path}): {e}")
