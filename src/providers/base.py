"""Base provider interface for image generation services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from enum import Enum

from pydantic import BaseModel, HttpUrl


class ProviderStatus(str, Enum):
    """Provider health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ImageGenerationParams(BaseModel):
    """Parameters for image generation."""

    prompt: str
    model: str
    width: int = 1024
    height: int = 1024
    seed: Optional[int] = None
    steps: int = 25
    guidance_scale: float = 7.5
    negative_prompt: Optional[str] = None
    style: Optional[str] = None
    quality: str = "standard"
    aspect_ratio: str = "1:1"
    additional_params: Dict[str, Any] = {}


class ImageResult(BaseModel):
    """Result from image generation."""

    url: HttpUrl
    width: int
    height: int
    file_size: Optional[int] = None
    format: str = "png"
    seed: Optional[int] = None
    model: str
    provider: str
    generation_time: float
    metadata: Dict[str, Any] = {}


class ProviderHealth(BaseModel):
    """Provider health status."""

    status: ProviderStatus
    message: str
    response_time: Optional[float] = None
    last_check: str
    metadata: Dict[str, Any] = {}


class BaseProvider(ABC):
    """Base class for image generation providers."""

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize provider.

        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self.name = self.__class__.__name__.replace("Provider", "").lower()

    @abstractmethod
    async def generate_image(
        self, params: ImageGenerationParams
    ) -> ImageResult:
        """Generate an image from parameters.

        Args:
            params: Image generation parameters

        Returns:
            Generated image result

        Raises:
            ProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def upscale_image(
        self, image_url: str, factor: int = 2, **kwargs: Any
    ) -> ImageResult:
        """Upscale an existing image.

        Args:
            image_url: URL of the image to upscale
            factor: Upscaling factor (2x, 4x, etc.)
            **kwargs: Additional parameters

        Returns:
            Upscaled image result

        Raises:
            ProviderError: If upscaling fails
        """
        pass

    @abstractmethod
    async def check_health(self) -> ProviderHealth:
        """Check provider health status.

        Returns:
            Provider health status
        """
        pass

    def get_supported_models(self) -> list[str]:
        """Get list of supported models.

        Returns:
            List of model names
        """
        return []

    def get_supported_styles(self) -> list[str]:
        """Get list of supported styles.

        Returns:
            List of style names
        """
        return []


class ProviderError(Exception):
    """Base exception for provider errors."""

    def __init__(
        self,
        message: str,
        provider: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize provider error.

        Args:
            message: Error message
            provider: Provider name
            error_code: Optional error code
            details: Optional error details
        """
        super().__init__(message)
        self.provider = provider
        self.error_code = error_code
        self.details = details or {}