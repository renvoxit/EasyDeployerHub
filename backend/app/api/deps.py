# ROLE:
# Dependency injection for API layer.
#
# RESPONSIBILITIES:
# - Provide shared dependencies for routes (db session, auth context).
# - Centralize FastAPI dependencies.
#
# MUST NOT:
# - Contain business logic.
# - Perform complex operations.
# - Call external services directly.
