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

import os
import shutil
import stat

from app.core.log_stream import append_log
from app.services.docker_engine import remove_container, remove_image


def _make_writable(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        raise


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
            shutil.rmtree(workspace_path, onerror=_make_writable)

            if os.path.exists(workspace_path):
                raise RuntimeError("workspace still exists after cleanup")

            append_log(deploy_id, f"Cleanup result: workspace removed ({workspace_path})")
        except Exception as e:
            append_log(deploy_id, f"Cleanup result: workspace remove failed ({workspace_path}): {e}")
