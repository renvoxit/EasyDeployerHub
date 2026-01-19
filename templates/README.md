# Templates

ROLE:
Reusable deployment templates used to generate runtime artifacts
(Dockerfiles, startup scripts, proxy configs).

RULES:
- Templates contain NO logic.
- Templates are rendered with provided context only.
- Templates must be deterministic and environment-agnostic.

WHAT BELONGS HERE:
- Dockerfile templates
- Startup scripts
- Proxy configuration templates

WHAT DOES NOT BELONG HERE:
- Python code
- Business rules
- Environment secrets
