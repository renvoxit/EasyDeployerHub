# ROLE:
# Centralized API error handling routes.
#
# RESPONSIBILITIES:
# - Define standardized error responses for the API.
# - Provide consistent error format across all endpoints.
# - Handle known application-level error cases.
#
# MUST:
# - Map internal errors to HTTP responses.
# - Use shared error schemas.
#
# MUST NOT:
# - Contain business logic.
# - Perform side effects.
# - Replace global exception handlers or middleware.
#
# NOTES:
# This file defines how errors are exposed to clients,
# not how errors are generated internally.
