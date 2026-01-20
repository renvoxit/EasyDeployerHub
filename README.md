# Easy Deployer Hub

Early-stage backend deploy platform.

Goal:  
GitHub repository → automatic build → running service with public URL.

---

## Status

Easy Deployer Hub is an early-stage prototype.

#### Current state

- Backend service is running and accepts HTTP requests.
- GitHub OAuth authentication flow is implemented and functional.
- The application successfully obtains a GitHub access token after authorization.
- Basic deployment orchestration primitives (statuses and logs) are present.

#### Next step

GitHub API integration:
Fetching authenticated user data and user repositories to enable repository selection for deployment.

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

Open an issue or discussion if interested.
