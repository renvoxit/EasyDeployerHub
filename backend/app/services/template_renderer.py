# ROLE:
# Deployment template rendering service.
#
# RESPONSIBILITIES:
# - Render Dockerfile and runtime templates.
# - Fill templates with analyzed project data.
#
# MUST NOT:
# - Decide which template to use.
# - Perform filesystem cleanup.
# - Execute Docker commands.
