# ROLE:
# User-related database operations.
#
# RESPONSIBILITIES:
# - Create, read, update user records.
#
# MUST NOT:
# - Perform authorization.
# - Contain business decisions.

from datetime import datetime
from uuid import uuid4

from app.db.session import get_conn


def get_user_by_github_id(github_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, github_id, login, name, email, avatar_url, html_url, created_at
        FROM users
        WHERE github_id = ?
        """,
        (github_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "github_id": row[1],
        "login": row[2],
        "name": row[3],
        "email": row[4],
        "avatar_url": row[5],
        "html_url": row[6],
        "created_at": row[7],
    }


def upsert_user_from_github(github_user: dict):
    existing = get_user_by_github_id(github_user["id"])

    conn = get_conn()
    cur = conn.cursor()

    if existing:
        cur.execute(
            """
            UPDATE users
            SET login = ?, name = ?, email = ?, avatar_url = ?, html_url = ?
            WHERE github_id = ?
            """,
            (
                github_user.get("login"),
                github_user.get("name"),
                github_user.get("email"),
                github_user.get("avatar_url"),
                github_user.get("html_url"),
                github_user["id"],
            ),
        )
        conn.commit()
        conn.close()

        return get_user_by_github_id(github_user["id"])

    user_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()

    cur.execute(
        """
        INSERT INTO users (
            id, github_id, login, name, email, avatar_url, html_url, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            github_user["id"],
            github_user.get("login"),
            github_user.get("name"),
            github_user.get("email"),
            github_user.get("avatar_url"),
            github_user.get("html_url"),
            created_at,
        ),
    )
    conn.commit()
    conn.close()

    return get_user_by_github_id(github_user["id"])
