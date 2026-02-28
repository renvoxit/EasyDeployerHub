# EasyDeployerHub

Backend-first deployment MVP.

Goal:

GitHub repository → automatic build → running service → public URL.

EasyDeployerHub is a modular deployment platform designed to build a minimal Heroku-like pipeline for personal and experimental projects.

The project focuses on clean orchestration, strict service boundaries, and incremental infrastructure integration.

---

## Project Status

EasyDeployerHub is currently a backend MVP with real GitHub integration and stubbed runtime infrastructure.

The architecture and API layer are real.
Infrastructure (Git clone, Docker, reverse proxy) remains simulated.

This allows stable system design before integrating heavy runtime components.

---

## Current State

The backend supports a complete end-to-end deployment flow:

`clone_repo → analyze_project → render_templates → build_image → run_container → expose_service`

The orchestration flow is real and modular.
Infrastructure-heavy steps are currently stubbed.

## Implemented:

### Deployment Layer

- FastAPI backend
- API-triggered deployment (POST /deploy)
- Deployment orchestrator coordinating all stages
- Modular service-based pipeline:
  - repo_cloner
  - analyzer
  - template_renderer
  - docker_engine (stub)
  - proxy_manager (stub)
- Deployment lifecycle tracking (running / success / failed)
- Stage-based deployment logs
- Deployment ID returned to client
- Stub-generated public URL
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

## What Is Stubbed

The following components simulate behavior but do not yet execute real infrastructure actions:
- Git clone (repo_cloner)
- Docker build / run (docker_engine)
- Reverse proxy routing (proxy_manager)
- Real public URL exposure
The orchestration is real; execution is mocked.

## API (Current)

Deployment:
`POST /deploy`

GitHub:
```
GET /github/me
GET /github/repos?page=&per_page=
```
Swagger UI:

`http://127.0.0.1:8000/docs`

## Current Phase

Backend MVP with GitHub API complete, infrastructure integration pending.

Next phase focuses on replacing stubs with real infrastructure components.

---

## Next Steps

1. Persist final deployment status and public URL
2. Add `GET /deploy/{id}` (status + logs)
3. Replace stubs with real implementations:
  - repo_cloner → real Git clone
  - docker_engine → Docker build / run
  - proxy_manager → Traefik routing
4. Infrastructure hardening (error handling, retries, timeouts)
5. Frontend integration

---

## Local Development (Backend)

Requirements:

- Python 3.11+
- Git

Run locally:

```
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
````

Server will be available at:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Swagger UI:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Contributing

This project is architecture-driven and modular by design.

Core orchestration boundaries should not be modified without discussion.

Good areas for contribution:

- Infrastructure integration
- Docker runtime implementation
- Proxy configuration
- Performance and error resilience
- Frontend dashboard

Open an issue before making structural changes.
