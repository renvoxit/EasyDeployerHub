# Security Model

This document describes the security boundaries and assumptions of the Easy Deployer Hub.
It defines what the system allows and what it explicitly restricts.

---

## Execution Isolation

- All user projects are executed inside isolated containers
- No project code is executed directly on the host system
- Each deployment runs in its own container instance

---

## Resource Limits

- CPU and memory limits are applied per container
- Disk usage is limited for build and runtime stages
- Long-running or stuck deployments can be terminated

---

## Network Restrictions

- Deployed containers expose only explicitly configured ports
- Internal services are not accessible from user containers
- Outbound network access may be restricted in future stages

---

## Secrets Handling

- Secrets are provided via environment variables
- Secrets are never stored in source code
- Secrets are not logged or exposed in build/runtime logs

---

## Repository Access

- Access to repositories is granted via GitHub OAuth
- Only repositories explicitly selected by the user are accessed
- Repository access tokens are stored securely and can be revoked

---

## Non-Goals

The system does not aim to provide:
- Full sandboxing against all possible container escapes
- Protection against malicious code logic inside containers
- Guarantees for untrusted production workloads

This platform is designed for development and early-stage use cases.
