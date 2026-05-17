# ROLE:
# Deployment template rendering service.
#
# RESPONSIBILITIES:
# - Render Dockerfile and runtime templates.
# - Fill templates with analyzed project data.
#
# MUST NOT:
# - Decide which template to use.
# - Perform filesystem cleanup.
# - Execute Docker commands.

import os
from pathlib import Path

from app.core.log_stream import append_log

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_ROOT = PROJECT_ROOT / "templates"

DEFAULT_PORTS = {
    "python-fastapi": 8000,
    "python-flask": 5000,
    "node": 3000,
    "react": 80,
    "static": 80,
}


def _render_template(template: str, context: dict[str, str | int]) -> str:
    rendered = template
    for key, value in context.items():
        rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
    return rendered


def _default_dockerfile(project_type: str, port: int) -> str:
    if project_type == "python-fastapi":
        return f"""FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

EXPOSE {port}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""

    if project_type == "python-flask":
        return f"""FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

EXPOSE {port}
ENV PORT={port}

CMD ["python", "app.py"]
"""

    if project_type == "node":
        return f"""FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE {port}
ENV PORT={port}

CMD ["npm", "start"]
"""

    if project_type == "react":
        return """FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
"""

    if project_type == "static":
        return """FROM nginx:1.27-alpine

COPY . /usr/share/nginx/html

EXPOSE 80
"""

    raise RuntimeError(f"Unsupported project type: {project_type}")


def render_templates(deploy_id: str, workspace_path: str, project_type: str) -> str:
    """
    Render the Dockerfile for a detected project type.
    """

    append_log(deploy_id, f"Rendering templates for: {project_type}")

    dockerfile_path = os.path.join(workspace_path, "Dockerfile")
    port = DEFAULT_PORTS.get(project_type)

    if port is None:
        raise RuntimeError(f"Unsupported project type: {project_type}")

    template_path = TEMPLATES_ROOT / project_type / "Dockerfile.j2"
    template = ""

    if template_path.exists():
        template = template_path.read_text(encoding="utf-8").strip()

    if template:
        dockerfile_content = _render_template(template, {"port": port})
    else:
        dockerfile_content = _default_dockerfile(project_type, port)

    with open(dockerfile_path, "w", encoding="utf-8") as f:
        f.write(dockerfile_content)

    append_log(deploy_id, f"Dockerfile created at: {dockerfile_path}")

    return dockerfile_path
