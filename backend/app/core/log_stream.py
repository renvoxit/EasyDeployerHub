# ROLE:
# Deployment log streaming logic.
#
# RESPONSIBILITIES:
# - Aggregate deployment logs.
# - Expose log stream interface.
# - Coordinate log flow between services and API.
#
# MUST NOT:
# - Generate logs.
# - Write logs to storage.
# - Depend on HTTP layer.

from pathlib import Path

LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def log_path(deploy_id: str) -> Path:
    return LOGS_DIR / f"{deploy_id}.log"


def append_log(deploy_id: str, line: str):
    with open(log_path(deploy_id), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_logs(deploy_id: str) -> str:
    path = log_path(deploy_id)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
