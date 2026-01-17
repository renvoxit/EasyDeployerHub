# Architecture Overview

This document describes the high-level architecture of the Easy Deployer Hub.
It focuses on system components and their responsibilities, not on implementation details.

---

## Core Components

### Backend API
The backend is the central control layer of the platform.

Responsibilities:
- User authentication (GitHub OAuth)
- Repository listing and selection
- Deployment request handling
- Deployment status tracking
- Project lifecycle management

The backend does not perform heavy deployment tasks directly.

---

### Worker
The worker is responsible for execution-heavy and time-consuming operations.

Responsibilities:
- Repository cloning
- Project analysis
- Deployment configuration generation
- Docker image build
- Container startup and cleanup

The worker operates asynchronously and processes jobs from a queue.

---

### Deployment Templates
Templates define how different types of projects are deployed.

Responsibilities:
- Provide base Dockerfile templates
- Define build and run strategies per project type
- Standardize deployment behavior

Templates are selected automatically based on project analysis.

---

### Container Runtime
Docker is used as the execution environment.

Responsibilities:
- Isolate deployed projects
- Control resource usage
- Provide reproducible execution

Each deployment runs in its own container.

---

### Reverse Proxy
The reverse proxy exposes deployed projects to the public.

Responsibilities:
- Route incoming traffic to running containers
- Assign and manage public URLs
- Handle HTTP/HTTPS termination

---

## Data Flow Summary

1. User interacts with the Backend API
2. Backend creates a deployment job
3. Worker processes the job
4. Container is built and started
5. Reverse proxy exposes the project
6. Backend reports status to the user

---

This architecture is designed to be modular and extensible.
Individual components can evolve independently as the system grows.
