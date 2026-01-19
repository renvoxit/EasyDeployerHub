# ROLE:
# Resource cleanup service.
#
# RESPONSIBILITIES:
# - Remove temporary files and resources.
# - Cleanup containers and artifacts after deployment.
#
# MUST NOT:
# - Decide when cleanup is triggered.
# - Affect active deployments.
# - Contain deployment logic.
