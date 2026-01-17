# API Overview

This document provides a high-level overview of the backend API.
It lists planned endpoints and their responsibilities without implementation details.

---

## Authentication

- `POST /auth/github`
  - Initiates GitHub OAuth flow

- `GET /auth/github/callback`
  - Handles OAuth callback and user session creation

---

## User

- `GET /me`
  - Returns information about the authenticated user

---

## Repositories

- `GET /repos`
  - Returns a list of GitHub repositories available to the user

---

## Deployments

- `POST /deploy`
  - Creates a new deployment job for a selected repository

- `GET /deploy/{id}`
  - Returns deployment status and metadata

- `GET /deploy/{id}/logs`
  - Streams build and runtime logs

---

## Projects

- `GET /projects`
  - Returns a list of deployed projects

- `POST /projects/{id}/restart`
  - Restarts a deployed project

- `DELETE /projects/{id}`
  - Stops and removes a deployed project

---

## Notes

- All endpoints require authentication unless stated otherwise
- API structure may evolve as the project progresses
- Detailed request/response schemas will be added in later stages
