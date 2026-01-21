# Easy Deployer Hub

Early-stage backend deploy platform.

Goal:  
GitHub repository → automatic build → running service with public URL.

---

## Status

Easy Deployer Hub is an early-stage prototype.

Currently implemented:
- Backend service (FastAPI)
- Basic deploy endpoint
- Deployment status tracking
- Deploy log streaming (in progress)

Planned next:
- GitHub OAuth
- Repository selection
- Real deployment pipeline

---

## What exists now
- FastAPI backend
- deployment lifecycle (running / success / failed)
- deployment logs via API
- persistent storage (SQLite)
- clean modular architecture

---

## Local development (backend)

Requirements:
- Python 3.11+
- Git

Run locally:

```
cd backend  
python -m venv venv

Activate venv (Windows):
venv\Scripts\activate

Activate venv (Linux / macOS):
source venv/bin/activate

pip install -r requirements.txt  
uvicorn app.main:app --reload  

Server will be available at:
http://127.0.0.1:8000
```

---

## API (current)

POST /deploy  
GET /status/{deploy_id}  
GET /logs/{deploy_id}

Example:
`curl -X POST http://127.0.0.1:8000/deploy`

---

## Roadmap (short)
- real git clone
- project analysis
- Docker build & run
- GitHub OAuth
- frontend dashboard

---

## Contributing

Issues labeled as `help wanted` are safe to work on and do not affect core architecture.
Early-stage contributions are welcome.

Looking for developers interested in:
- backend infrastructure
- deployment systems
- Docker & automation

Open an issue if interested.
