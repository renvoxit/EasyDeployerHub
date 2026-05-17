# EasyDeployerHub

Backend-first deployment MVP.

Goal:

GitHub repository → automatic build → running service → public URL.

EasyDeployerHub is a modular deployment platform designed to build a minimal Heroku-like pipeline for personal and experimental projects.

The project focuses on clean orchestration, strict service boundaries, and incremental infrastructure integration.

---

## Project Status

EasyDeployerHub is currently a backend MVP with a working orchestration flow and local Docker deployment.

Core backend components are implemented and operational:

- Git repository cloning
- Deployment request handling
- Deployment status tracking
- Stage-based deployment logs
- Docker image build
- Docker container execution
- Local port exposure
- GitHub OAuth and repository access
- Deployment persistence

Reverse proxy routing and public internet URL exposure are still pending.
The system is useful for backend integration work, but it is not yet a production deployment platform.

---

## Current State

The backend exposes a complete deployment orchestration flow:

`clone_repo → analyze_project → render_templates → build_image → run_container → expose_service`

The orchestration flow is real and modular.
Repository cloning is real.
Project analysis is basic, Docker build/run is real, and proxy exposure currently returns a local Docker port URL.

## Implemented:

### Deployment Layer

- FastAPI backend
- API-triggered deployment (`POST /deploy`)
- Deployment list endpoint (`GET /deploy`)
- Deployment detail endpoint (`GET /deploy/{deploy_id}`)
- Deployment orchestrator coordinating all stages
- Modular service-based pipeline:
  - repo_cloner
  - analyzer
  - template_renderer
  - docker_engine
  - proxy_manager
- Deployment lifecycle tracking (pending / running / success / failed)
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

## What Is Stubbed

The following components simulate behavior but do not yet execute real infrastructure actions:
- Advanced project analysis (analyzer)
- Reverse proxy domain routing (proxy_manager)
- Real public URL exposure
The orchestration, repository cloning, Docker image build, and Docker container startup are real.

## API (Current)

Deployment:
```
GET /deploy
GET /deploy/{deploy_id}
GET /deploy/status/{deploy_id}
GET /deploy/logs/{deploy_id}
POST /deploy
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

Backend MVP with local Docker deployment.

Next phase focuses on replacing local port exposure with Traefik/Nginx routing and improving project detection.

---

## Next Steps

1. Replace local port exposure with real Traefik/Nginx routing
2. Improve project detection and runtime command detection
3. Add deployment lifecycle management (restart / stop / delete)
4. Add resource cleanup
5. Add security isolation and resource limits
6. Build frontend dashboard after API contracts stabilize

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

Run tests:

```
pip install -r backend/requirements.txt
pytest
```

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
