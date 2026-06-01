# ROLE:
# Deployment-related database operations.
#
# RESPONSIBILITIES:
# - Persist deployment state and metadata.
#
# MUST NOT:
# - Control deployment workflow.
# - Interact with external systems.

from datetime import datetime

from app.db.session import get_conn


def create_deployment(deploy_id: str, status: str, repo_url: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deployments (id, status, repo_url, public_url, created_at) VALUES (?, ?, ?, ?, ?)",
        (deploy_id, status, repo_url, None, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def update_deployment_status(deploy_id: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE deployments SET status = ? WHERE id = ?",
        (status, deploy_id)
    )
    conn.commit()
    conn.close()


def update_deployment_result(deploy_id: str, status: str, public_url: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE deployments SET status = ?, public_url = ? WHERE id = ?",
        (status, public_url, deploy_id)
    )
    conn.commit()
    conn.close()


def update_deployment_runtime(
    deploy_id: str,
    workspace_path: str | None = None,
    image_tag: str | None = None,
    container_id: str | None = None,
):
    values = []
    assignments = []

    if workspace_path is not None:
        assignments.append("workspace_path = ?")
        values.append(workspace_path)

    if image_tag is not None:
        assignments.append("image_tag = ?")
        values.append(image_tag)

    if container_id is not None:
        assignments.append("container_id = ?")
        values.append(container_id)

    if not assignments:
        return

    values.append(deploy_id)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        f"UPDATE deployments SET {', '.join(assignments)} WHERE id = ?",
        values,
    )
    conn.commit()
    conn.close()


def clear_deployment_runtime(deploy_id: str, clear_public_url: bool = False):
    conn = get_conn()
    cur = conn.cursor()

    if clear_public_url:
        cur.execute(
            """
            UPDATE deployments
            SET workspace_path = NULL, image_tag = NULL, container_id = NULL, public_url = NULL
            WHERE id = ?
            """,
            (deploy_id,),
        )
    else:
        cur.execute(
            """
            UPDATE deployments
            SET workspace_path = NULL, image_tag = NULL, container_id = NULL
            WHERE id = ?
            """,
            (deploy_id,),
        )

    conn.commit()
    conn.close()


def get_deployment(deploy_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, status, repo_url, public_url, created_at, workspace_path, image_tag, container_id
        FROM deployments
        WHERE id = ?
        """,
        (deploy_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "deploy_id": row[0],
        "status": row[1],
        "repo_url": row[2],
        "public_url": row[3],
        "created_at": row[4],
        "workspace_path": row[5],
        "image_tag": row[6],
        "container_id": row[7],
    }


def list_deployments():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, status, repo_url, public_url, created_at, workspace_path, image_tag, container_id
        FROM deployments
        ORDER BY created_at DESC
        """
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "deploy_id": row[0],
            "status": row[1],
            "repo_url": row[2],
            "public_url": row[3],
            "created_at": row[4],
            "workspace_path": row[5],
            "image_tag": row[6],
            "container_id": row[7],
        }
        for row in rows
    ]
