# EasyDeployerHub

Early-stage deployment backend MVP.

Goal:

GitHub repository → automatic build → running service → public URL.

EasyDeployerHub is a backend-first deployment platform focused on building a minimal Heroku-like pipeline for personal and experimental projects.

---

## Project Status

EasyDeployerHub is currently a **skeleton MVP with stubbed runtime**.

The core deployment pipeline is implemented and functional in simulated form.

This phase focuses on architecture, orchestration flow, and system boundaries before integrating real infrastructure.

---

## Current State

The backend already supports a full end-to-end deployment flow:

```

clone_repo → analyze_project → render_templates → build_image → run_container → expose_service

````

### Implemented:

- FastAPI backend running locally and accepting HTTP requests
- API endpoint to trigger deployments (`POST /deploy`)
- Deployment orchestrator coordinating all stages
- Modular service architecture:
  - repo_cloner
  - analyzer
  - template_renderer
  - docker_engine
  - proxy_manager
- Deployment lifecycle tracking:
  - running / success / failed
- Centralized deployment logs per stage
- Deployment ID returned to client
- Public URL generated (stub)
- Persistent storage (SQLite/Postgres depending on environment)
- Clean separation between orchestration and services

All heavy operations (Git clone, Docker build/run, proxy routing) are currently implemented as **stubs**.

Architecture is real. Infrastructure is mocked.

This allows rapid iteration on system design before integrating Docker, GitHub API, and Traefik.

---

## What Exists Now

- FastAPI backend
- API-triggered deployment flow
- Deployment orchestrator
- Service-based pipeline
- Deployment logs
- Deployment lifecycle states
- Database persistence
- Modular backend architecture

This already forms a working MVP skeleton.

---

## Next Steps

Immediate priorities:

1. Persist `public_url` and final deployment status to database
2. Add `GET /deploy/{id}` endpoint (status + logs)
3. Replace stubs with real implementations:
   - repo_cloner → real Git clone
   - docker_engine → docker build / run
   - proxy_manager → Traefik routing
4. GitHub API integration:
   - fetch authenticated user
   - list repositories
   - enable repository selection
5. Frontend wiring

Current phase: **Skeleton MVP with stubbed runtime**

Next phase: **Real infrastructure integration**

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

## API (Current)

Trigger deployment:

```
POST /deploy
```

Returns:

```json
{
  "deploy_id": "...",
  "status": "running"
}
```

Planned:

```
GET /deploy/{deploy_id}
```

---

## Roadmap (Short)

* real git clone
* project analysis
* Docker build & run
* Traefik routing
* GitHub API integration
* frontend dashboard

---

## Contributing

This project is early-stage and architecture-driven.

Issues labeled `help wanted` are safe to work on and do not affect core design.

Looking for contributors interested in:

* backend infrastructure
* deployment systems
* Docker & automation

Open an issue or discussion if interested.
