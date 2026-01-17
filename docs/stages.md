# Development Stages

This document describes the development stages of the Easy Deployer Hub project.
Each stage represents a completed state of the system, not individual tasks.

Current stage is marked explicitly.

---

## Stage 1 — Backend Skeleton -> CURRENT
**Status:** 

- Backend service exists and can be started
- Basic HTTP API is available
- Configuration and environment handling are defined

At this stage, the system does not deploy projects yet.
It only provides a stable foundation for further development.

---

## Stage 2 — GitHub Integration

- GitHub OAuth authentication
- Access to user repositories via GitHub API
- User identity linked to GitHub account

At this stage, the system can interact with real user repositories.

---

## Stage 3 — Repository Intake

- Selection of a repository for deployment
- Repository cloning into a temporary workspace
- Basic validation of repository content

At this stage, the system can fetch and prepare user code.

---

## Stage 4 — Project Analysis

- Automatic detection of project type (frontend, backend, static, etc.)
- Detection of build and run requirements
- Port and runtime identification

At this stage, the system understands how a project should be executed.

---

## Stage 5 — Deployment Configuration Generation

- Automatic generation of Dockerfile
- Selection of deployment templates
- Preparation of runtime configuration

At this stage, projects are ready for containerization.

---

## Stage 6 — Build and Run

- Docker image build
- Container startup
- Environment variable injection

At this stage, projects are actually running on the server.

---

## Stage 7 — Deployment Orchestration

- Asynchronous deployment jobs
- Queue-based execution
- Deployment status tracking

At this stage, multiple deployments can be handled reliably.

---

## Stage 8 — Logs and Visibility

- Real-time build and runtime logs
- Error reporting
- Deployment progress visibility

At this stage, users can see what is happening during deployment.

---

## Stage 9 — Public Access

- Reverse proxy configuration
- Public URL generation
- Domain routing to running containers

At this stage, deployed projects are accessible from the internet.

---

## Stage 10 — Project Lifecycle Management

- List of deployed projects
- Restart, stop, and delete actions
- Resource cleanup

At this stage, users can fully manage their deployments.

---

## Stage 11 — Security and Limits

- Container isolation
- Resource limits
- Secret handling via environment variables

At this stage, the platform is safe for untrusted code.

---

## Stage 12 — Production Platform

- Monitoring
- Stability improvements
- Production readiness

At this stage, the system operates as a full deployment platform.
