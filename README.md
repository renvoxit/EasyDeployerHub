# EasyDeployerHub

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Docker](https://img.shields.io/badge/Docker-local_deploy-blue)
![Status](https://img.shields.io/badge/status-backend_MVP-orange)
![Production](https://img.shields.io/badge/production-not_ready-red)

Open-source mini deployment platform that deploys GitHub repositories locally with Docker.

**Flow:** GitHub repository → clone → analyze → generate Dockerfile → build image → run container → local URL / Traefik route.

EasyDeployerHub is a backend-first deployment MVP designed to show how a minimal Heroku-like deployment pipeline works internally.

It focuses on clean orchestration, modular service boundaries, Docker-based runtime execution, deployment status tracking, logs, and incremental infrastructure integration.

> Not production-ready yet. Currently functional as a local Docker deployment MVP.

---

## Project Status

EasyDeployerHub is currently a backend MVP with a working orchestration flow and local Docker deployment.

Core backend components are implemented and operational:

- Git repository cloning
- Deployment request handling
- Deployment status tracking
- Deployment lifecycle endpoints
- Deployment failure reason tracking
- Deployment diagnostics endpoint
- Stage-based deployment logs
- Docker image build
- Docker container execution
- Local port exposure
- Traefik label generation for deployed containers
- GitHub OAuth and repository access
- Deployment persistence

Traefik routing is configured when the proxy service is running.
Public internet URL exposure is still pending.
The system is useful for backend integration work, but it is not yet a production deployment platform.

---

## Current State

The backend exposes a complete deployment orchestration flow:

`clone_repo → analyze_project → render_templates → build_image → run_container → expose_service`

The orchestration flow is real and modular.
Repository cloning is real.
Project analysis is basic, Docker build/run is real, and proxy exposure returns a Traefik URL when available or a direct local Docker port URL as fallback.

## Why this project

EasyDeployerHub is a practical backend/devops project for learning how deployment platforms work internally.

It combines:

- GitHub OAuth and repository access
- Repository cloning and validation
- Basic project type detection
- Dockerfile generation from templates
- Docker image build and container startup
- Deployment status tracking
- Stage-based logs
- SQLite/Postgres persistence
- Local routing with Traefik
- Modular backend orchestration

The project is useful as a portfolio-grade backend system and as a learning project for deployment infrastructure.

## Implemented:

### Deployment Layer

- FastAPI backend
- API-triggered deployment (`POST /deploy`)
- Deployment list endpoint (`GET /deploy`)
- Deployment detail endpoint (`GET /deploy/{deploy_id}`)
- Deployment stop endpoint (`POST /deploy/{deploy_id}/stop`)
- Deployment restart endpoint (`POST /deploy/{deploy_id}/restart`)
- Deployment delete endpoint (`DELETE /deploy/{deploy_id}`)
- Deployment diagnostics endpoint (`GET /deploy/{deploy_id}/diagnostics`)
- Deployment orchestrator coordinating all stages
- Modular service-based pipeline:
  - repo_cloner
  - analyzer
  - template_renderer
  - docker_engine
  - proxy_manager
- Deployment lifecycle tracking (pending / running / success / failed / stopped / deleted)
- Runtime metadata persistence (`workspace_path`, `image_tag`, `container_id`)
- Failure metadata persistence (`failure_stage`, `failure_reason`)
- Resource consistency diagnostics
- Best-effort cleanup on failed deploy
- Runtime HTTP health check with timeout
- Stage-based deployment logs
- Deployment ID returned to client
- Local Docker URL returned to client
- Database persistence (SQLite / Postgres)
- Clear separation between orchestration and services

### GitHub Integration Layer

- GitHub OAuth authentication flow
- Access token exchange
- Centralized token dependency (`get_token`)
- `GET /github/me` endpoint
- `GET /github/repos` endpoint
- Pagination support (`page, per_page`)
- Link header parsing for total count estimation
- Typed Pydantic response schemas
- Clean error handling (401 / 502 / 500)
- Swagger documentation for all endpoints

---

## What Is Partial

The following components exist but are still limited:

- Project analysis: basic detection only, not full runtime intelligence
- Internet-facing domain routing: local Traefik routing works, production domains are not ready
- HTTPS termination: not implemented yet

## Demo Flow

Start the backend and send a deployment request:

```
curl -X POST http://127.0.0.1:8000/deploy \
  -H "Content-Type: application/json" \
  -d "{\"repo_url\": \"https://github.com/user/repo.git\"}"
```
Check deployment status:

`curl http://127.0.0.1:8000/deploy/{deploy_id}`

Get deployment logs:

`curl http://127.0.0.1:8000/deploy/logs/{deploy_id}`

When Traefik is running, deployments are exposed through a local routed URL like:

`http://localhost:8080/deployments/<deploy-id-prefix>/`

If Traefik is not running, EasyDeployerHub falls back to a direct local Docker port URL:

`http://127.0.0.1:<port>`

## API (Current)

Deployment:
```
GET /deploy
GET /deploy/{deploy_id}
GET /deploy/status/{deploy_id}
GET /deploy/logs/{deploy_id}
GET /deploy/{deploy_id}/diagnostics
POST /deploy
POST /deploy/{deploy_id}/stop
POST /deploy/{deploy_id}/restart
DELETE /deploy/{deploy_id}
```

`POST /deploy` expects:

```
{
  "repo_url": "https://github.com/user/repo.git"
}
```

GitHub:
```
GET /github/me
GET /github/repos?page=&per_page=
```
Swagger UI:

`http://127.0.0.1:8000/docs`

## Current Phase

Backend MVP with local Docker deployment, partial Traefik routing, and lifecycle management.

Lifecycle management is implemented, covered by unit tests, and validated with real Docker smoke.
Runtime reliability and failure reason normalization are implemented with unit coverage.
Resource diagnostics and consistency audit are implemented with unit coverage.

Next phase focuses on completing real Docker failure-path smoke validation, then public routing, security limits, and improved project detection.

---

## Roadmap

### Now — Runtime Reliability Validation

Current focus:

- Validate real Docker failure paths and persisted `failure_stage` / `failure_reason`
- Confirm failed deployments clean up created resources
- Validate diagnostics against real Docker mismatch scenarios

### Next

- Improve project analysis and runtime detection
- Add environment variable support
- Improve Docker build/runtime logs
- Add worker/queue-based deployment execution
- Add better deployment error reporting
- Complete public routing with domains and HTTPS

### Later

- Frontend dashboard
- Security isolation for untrusted code
- Resource limits
- Monitoring and production hardening

---

## Local Development (Backend)

Requirements:

- Python 3.11+
- Git

Run locally:

~~~bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
~~~

Run tests:

~~~bash
pip install -r backend/requirements.txt
python -m pytest tests -vv -s --timeout=60
~~~

Server will be available at:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

---

## Contributing

EasyDeployerHub is architecture-driven and modular by design.

Please open an issue before making structural changes.

Good first contribution areas:

- Documentation improvements
- Analyzer fixture tests
- Deployment API read endpoint tests
- Local Traefik routing documentation
- Deployment status constants
- Cleanup design notes

Core orchestration boundaries should not be modified without discussion.

Before opening a pull request:

1. Keep changes focused and small.
2. Do not mix unrelated features.
3. Run tests before submitting.
4. Update documentation if behavior changes.

## Author

Built by Renvoxit Systems.

Portfolio: https://renvoxit.com
