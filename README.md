# EasyDeployerHub

Backend-first deployment MVP.

Goal:

GitHub repository → automatic build → running service → public URL.

EasyDeployerHub is a modular deployment platform designed to build a minimal Heroku-like pipeline for personal and experimental projects.

The project focuses on clean orchestration, strict service boundaries, and incremental infrastructure integration.

---

## Project Status

EasyDeployerHub is currently a backend MVP with a working end-to-end deployment pipeline.

Core infrastructure components are implemented and operational:

- Git repository cloning
- Project analysis
- Docker image build
- Container execution
- Reverse proxy exposure
- Public URL generation

The system is functional but still lacks production-level stability,
security, and lifecycle management features.

---

## Current State

The backend supports a complete end-to-end deployment flow:

`clone_repo → analyze_project → render_templates → build_image → run_container → expose_service`

The orchestration flow is real and modular.
Infrastructure components are partially implemented.
Core deployment pipeline is operational end-to-end.

## Implemented:

### Deployment Layer

- FastAPI backend
- API-triggered deployment (POST /deploy)
- Deployment orchestrator coordinating all stages
- Modular service-based pipeline:
  - repo_cloner
  - analyzer
  - template_renderer
  - docker_engine
  - proxy_manager
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

1. Deployment lifecycle management (restart / stop / delete)
2. Deployment list endpoint
3. Resource cleanup
4. Security isolation
5. Resource limits
6. Production hardening
7. Frontend dashboard

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
