# Development Stages

This document describes the development stages of the Easy Deployer Hub project.
Each stage represents a completed state of the system, not individual tasks.

Current stage is marked explicitly.

---

## Stage 1 — Backend Skeleton -> DONE
**Status:** 

- Backend service exists and can be started
- Basic HTTP API is available
- Configuration and environment handling are defined

At this stage, the system does not deploy projects yet.
It only provides a stable foundation for further development.

---

## Stage 2 — GitHub Integration -> DONE

- GitHub OAuth authentication
- Access to user repositories via GitHub API
- User identity linked to GitHub account

At this stage, the system can interact with real user repositories.

---

## Stage 3 — Repository Intake -> DONE

- Selection of a repository for deployment
- Repository cloning into a temporary workspace
- Basic validation of repository content

At this stage, the system can fetch and prepare user code.

---

## Stage 4 — Project Analysis -> PARTIAL

- Automatic detection of project type (frontend, backend, static, etc.)
- Detection of build and run requirements
- Port and runtime identification

Current implementation uses a hardcoded analyzer stub.
At this stage, the system has the boundary for analysis but does not yet fully understand arbitrary projects.

---

## Stage 5 — Deployment Configuration Generation -> PARTIAL

- Automatic generation of Dockerfile
- Selection of deployment templates
- Preparation of runtime configuration

Current implementation writes a basic Dockerfile stub.
At this stage, the system has the template-rendering boundary but not complete runtime-specific generation.

---

## Stage 6 — Build and Run -> DONE

- Docker image build
- Container startup
- Environment variable injection

Current implementation builds Docker images and starts containers with local port mapping.
At this stage, projects can run locally through a generated `http://127.0.0.1:<port>` URL.

---

## Stage 7 — Deployment Orchestration -> PARTIAL

- Asynchronous deployment jobs
- Queue-based execution
- Deployment status tracking

Current implementation uses a backend background thread and deployment status tracking.
A dedicated worker/queue system is still planned.

---

## Stage 8 — Logs and Visibility -> PARTIAL

- Real-time build and runtime logs
- Error reporting
- Deployment progress visibility

Current implementation stores stage-based deployment logs.
Real Docker build/runtime log streaming is still planned.

---

## Stage 9 — Public Access -> PARTIAL

- Reverse proxy configuration
- Public URL generation
- Domain routing to running containers

Current implementation configures Traefik labels for deployed containers and returns a routed URL when `edh-proxy` is running.
If the proxy is not running, the system falls back to the direct local Docker port URL.
Internet-facing domains and HTTPS are still required before deployed projects are publicly accessible outside the host.

---

## Stabilization Stage — Backend MVP Alignment

- Keep API contracts stable
- Persist repository metadata for deployments
- Provide deployment listing and detail endpoints
- Keep documentation aligned with implemented behavior
- Keep tests runnable before adding larger features

At this stage, the MVP is being prepared for real infrastructure integration.

---

## Stage 10 — Project Lifecycle Management -> DONE

- List of deployed projects
- Restart, stop, and delete actions
- Resource cleanup

Current implementation includes lifecycle endpoints for stop, restart, and delete.
Runtime metadata is persisted for each deployment (`workspace_path`, `image_tag`, `container_id`).
Failed deployments attempt best-effort cleanup of created resources.
Unit coverage is in place.

Real Docker lifecycle smoke validation passed.

Validated behavior:

- `docker info` succeeds
- A real deployment stores `workspace_path`, `image_tag`, and `container_id`
- `POST /deploy/{id}/stop` stops the container and sets status to `stopped`
- `POST /deploy/{id}/restart` starts the container again, passes HTTP health check, and sets status to `success`
- `DELETE /deploy/{id}` removes container, image, workspace, and sets status to `deleted`

---

## Stage 11 — Runtime Reliability + Failure Reason Normalization -> DONE

- Persist normalized deployment failure details
- Track failure stage and reason
- Improve runtime health checks
- Cleanup resources after failed deployments
- Make deployment logs explain stage starts, failures, reasons, and cleanup results

Current implementation stores `failure_stage` and `failure_reason` for failed deployments.
Failure stages are normalized to `clone`, `analyze`, `render_template`, `docker_build`, `docker_run`, `health_check`, `proxy`, `cleanup`, or `unknown`.
Runtime health checks retry until timeout and only accept HTTP `200-399` as success.
Failed deployments attempt best-effort cleanup and log cleanup results.
Unit coverage is in place.

Status: implemented with unit coverage; real Docker failure-path smoke validation is still recommended.

---

## Stage 12 — Resource Tracking + Consistency Audit -> DONE

- Inspect persisted deployment state
- Inspect real Docker container and image state
- Inspect workspace filesystem state
- Report deployment health and consistency issues

Current implementation includes `GET /deploy/{id}/diagnostics`.
Diagnostics return DB status, Docker container existence/state, image existence, workspace existence, public URL, health check status, and detected inconsistencies.

Detected inconsistencies include:

- `success` but container missing
- `success` but container not running
- `success` but health check fails
- `deleted` but container, image, or workspace still exists
- `stopped` but container running
- `failed` but failure stage/reason missing
- active deployment but workspace missing

Validation note:

- Unit tests: 28 passed
- Real diagnostics smoke passed
- Success diagnostics OK
- Stopped diagnostics OK
- Deleted diagnostics OK
- Inconsistencies are empty in expected valid states

Status: CLOSED/DONE.

---

## Stage 13 — Security and Limits

- Container isolation
- Resource limits
- Secret handling via environment variables

At this stage, the platform is safe for untrusted code.

---

## Stage 14 — Production Platform

- Monitoring
- Stability improvements
- Production readiness

At this stage, the system operates as a full deployment platform.

## Common Backend Deployment Issues

- Build errors (dependency failures, syntax issues)
- Missing or incorrect port configuration (wrong port, binding to localhost)
- Runtime crashes (startup exceptions, OOM kills)
- Environment variable issues (missing keys, typos)
- Database connection failures or unapplied migrations
- Health check timeouts or misconfiguration
