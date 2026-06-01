# Templates

This directory contains deterministic templates used to generate deployment
runtime artifacts such as Dockerfiles, startup scripts, and proxy configuration.

Templates are intentionally simple. They should describe generated files, not
decide deployment behavior.

## Rules

- Keep templates deterministic for the same render context.
- Do not place business logic in template files.
- Do not store secrets, tokens, or environment-specific credentials here.
- Keep generated artifacts easy to inspect and debug.
- Prefer explicit template variables over hidden assumptions.

## Belongs Here

- Dockerfile templates.
- Runtime startup scripts.
- Proxy or routing configuration templates.
- Small generated configuration files required by deployment stages.

## Does Not Belong Here

- Python application code.
- Deployment orchestration rules.
- Analyzer logic.
- Secret values.
- Environment-specific local configuration.
