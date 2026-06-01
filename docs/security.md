# Security

This document describes the current security assumptions for EasyDeployerHub.
The project is a local deployment MVP, so the notes below are meant to make its
current boundaries clear.

## Supported Use Case

EasyDeployerHub is designed for local development, portfolio demonstration, and
controlled testing of deployment workflows. It can build and run repositories in
Docker containers. Production hardening is still future work.

## Current Boundaries

- Repository code is built and executed inside Docker containers.
- Project code is not intentionally executed directly on the host.
- Deployments are tracked with lifecycle state, logs, runtime metadata, and
  failure information.
- Containers can be stopped, restarted, deleted, and inspected through backend
  lifecycle endpoints.
- Traefik labels are generated for local routing when the proxy is available.

## Secrets

Secrets should be supplied through environment variables or local configuration
outside source control. They must not be committed to the repository, embedded
in templates, or written to deployment logs.

GitHub access is handled through OAuth. Tokens should be scoped as narrowly as
possible and revoked when no longer needed.

## Known Limitations

The current MVP does not claim to provide:

- complete protection against container escape vulnerabilities;
- hardened sandboxing for unknown third-party repositories;
- production-grade tenant isolation;
- public HTTPS and domain management;
- comprehensive resource governance;
- secret scanning or policy enforcement for deployed repositories.

Only run repositories you trust or can safely evaluate in your local Docker
environment.

## Reporting Security Issues

Please do not open a public issue for sensitive security reports. Contact the
maintainer privately with a concise description, reproduction steps, affected
area, and any relevant logs with secrets removed.

For non-sensitive hardening ideas, open a normal issue and describe the threat
model or failure mode the change is intended to address.
