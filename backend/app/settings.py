# ROLE:
# Centralized backend configuration.
#
# RESPONSIBILITIES:
# - Read environment variables.
# - Validate required settings.
# - Expose configuration to other modules.
#
# MUST NOT:
# - Perform side effects.
# - Create connections.
# - Read env vars outside this file.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str

    class Config:
        env_file = ".env"


settings = Settings()
