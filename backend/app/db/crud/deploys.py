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


def create_deployment(deploy_id: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deployments (id, status, public_url, created_at) VALUES (?, ?, ?, ?)",
        (deploy_id, status, None, datetime.utcnow().isoformat())
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


def get_deployment(deploy_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, status, public_url, created_at FROM deployments WHERE id = ?",
        (deploy_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "deploy_id": row[0],
        "status": row[1],
        "public_url": row[2],
        "created_at": row[3],
    }
