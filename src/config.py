"""Configuration settings for the MCP Visual Design Service."""

import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Service configuration
    host: str = Field(default="0.0.0.0", env="MCP_VISUAL_SERVICE_HOST")
    port: int = Field(default=8004, env="MCP_VISUAL_SERVICE_PORT")
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Provider configuration
    fal_api_key: Optional[str] = Field(default=None, env="FAL_API_KEY")
    fal_text_to_image_model: str = Field(
        default="fal-ai/flux/schnell", env="FAL_TEXT_TO_IMAGE_MODEL"
    )
    fal_image_to_image_model: str = Field(
        default="fal-ai/flux/schnell", env="FAL_IMAGE_TO_IMAGE_MODEL"
    )

    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_default_model: str = Field(
        default="black-forest-labs/flux-1.1-pro", env="OPENROUTER_DEFAULT_MODEL"
    )
    openrouter_backup_model: str = Field(
        default="black-forest-labs/flux-1-schnell", env="OPENROUTER_BACKUP_MODEL"
    )

    # PayloadCMS configuration
    payloadcms_api_url: str = Field(
        default="http://localhost:3000/api", env="PAYLOADCMS_API_URL"
    )
    payloadcms_api_key: Optional[str] = Field(default=None, env="PAYLOADCMS_API_KEY")

    # Optional features
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    websocket_enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    payloadcms_websocket_url: Optional[str] = Field(
        default=None, env="PAYLOADCMS_WEBSOCKET_URL"
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()