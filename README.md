# EasyDeployerHub

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Docker](https://img.shields.io/badge/Docker-local_deploy-blue)
![Status](https://img.shields.io/badge/status-backend_MVP-orange)
![Production](https://img.shields.io/badge/production-not_ready-red)

EasyDeployerHub is a backend-first deployment platform MVP for running GitHub
repositories locally through a Docker-based deployment pipeline.

Flow:

```text
GitHub repository -> clone -> analyze -> render templates -> build image -> run container -> expose URL
```

The project is designed to make deployment orchestration easy to inspect:
repository access, project analysis, Dockerfile generation, image builds,
container runtime, deployment status, logs, diagnostics, and local routing are
handled as separate backend services.

> EasyDeployerHub is currently a local development MVP. It is useful for
> learning, testing, and demonstrating deployment workflows.

## Current Status

The backend supports a complete local deployment flow:

```text
clone_repo -> analyze_project -> render_templates -> build_image -> run_container -> expose_service
```

Implemented capabilities:

- FastAPI backend API.
- GitHub OAuth and repository access.
- Repository cloning and validation.
- Basic project analysis.
- Template-based Dockerfile generation.
- Docker image build and container startup.
- Local port exposure.
- Traefik label generation for routed local deployments.
- Deployment lifecycle actions: create, inspect, stop, restart, and delete.
- Deployment status tracking: pending, running, success, failed, stopped, and deleted.
- Stage-based deployment logs.
- Failure stage and failure reason persistence.
- Runtime metadata persistence.
- Deployment diagnostics and resource consistency checks.
- SQLite/Postgres persistence.
- Unit coverage for lifecycle, diagnostics, and failure handling.
- Real Docker smoke validation for key deployment paths.

Traefik routing is used when the proxy service is running. If Traefik is not
available, deployments fall back to a direct local Docker port URL.

## Architecture

The backend is organized around small deployment services coordinated by an
orchestrator:

- `repo_cloner` - clones the selected repository into a workspace.
- `analyzer` - detects basic project characteristics.
- `template_renderer` - renders deployment artifacts from templates.
- `docker_engine` - builds images and manages containers.
- `proxy_manager` - prepares local routing metadata.

This separation keeps the deployment pipeline traceable and makes failures
easier to diagnose by stage.

## API Overview

Deployment endpoints:

```text
GET    /deploy
GET    /deploy/{deploy_id}
GET    /deploy/status/{deploy_id}
GET    /deploy/logs/{deploy_id}
GET    /deploy/{deploy_id}/diagnostics
POST   /deploy
POST   /deploy/{deploy_id}/stop
POST   /deploy/{deploy_id}/restart
DELETE /deploy/{deploy_id}
```

GitHub endpoints:

```text
GET /github/me
GET /github/repos?page=&per_page=
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Example

Start a deployment:

```bash
curl -X POST http://127.0.0.1:8000/deploy \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\": \"https://github.com/user/repo.git\"}"
```

Check deployment status:

```bash
curl http://127.0.0.1:8000/deploy/{deploy_id}
```

Read deployment logs:

```bash
curl http://127.0.0.1:8000/deploy/logs/{deploy_id}
```

When Traefik is running, deployments are exposed through a local routed URL:

```text
http://localhost:8080/deployments/<deploy-id-prefix>/
```

Without Traefik, the backend returns a direct local Docker URL:

```text
http://127.0.0.1:<port>
```

## Local Development

Requirements:

- Python 3.11+
- Git
- Docker

Create a backend environment:

```bash
cd backend
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source venv/bin/activate
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests from the repository root:

```bash
pip install -r backend/requirements.txt
python -m pytest tests -vv -s --timeout=60
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Roadmap

Near-term focus:

- Validate additional real Docker failure paths.
- Improve project analysis and runtime detection.
- Add environment variable support for deployments.
- Improve Docker build and runtime logs.
- Add worker or queue-based deployment execution.
- Complete public routing with domains and HTTPS.

Later work:

- Frontend dashboard improvements.
- Stronger security isolation for third-party code.
- Resource limits and policy controls.
- Monitoring and production hardening.

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Deployment stages](docs/stages.md)
- [Security](docs/security.md)
- [Contributing](docs/contributing.md)

## Contributing

Contributions are welcome. Please keep pull requests focused, include tests or
documentation when relevant, and read [docs/contributing.md](docs/contributing.md)
before opening a pull request.

## License

MIT. See [LICENSE](LICENSE) for details.

## Author

Built by Renvoxit Systems.

Portfolio: https://renvoxit.com
