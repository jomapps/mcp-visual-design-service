"""Test configuration and fixtures."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.providers.base import ImageResult, ProviderHealth, ProviderStatus
from src.config import Settings


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        environment="test",
        fal_api_key="test-fal-key",
        openrouter_api_key="test-openrouter-key",
        payloadcms_api_url="http://test-cms.local/api",
        payloadcms_api_key="test-cms-key",
    )


@pytest.fixture
def mock_image_result():
    """Mock image generation result."""
    return ImageResult(
        url="https://example.com/test-image.png",
        width=1024,
        height=1024,
        file_size=1024*1024,
        format="png",
        seed=12345,
        model="test-model",
        provider="test-provider",
        generation_time=5.0,
        metadata={"test": True},
    )


@pytest.fixture
def mock_provider_health():
    """Mock provider health status."""
    return ProviderHealth(
        status=ProviderStatus.HEALTHY,
        message="Test provider is healthy",
        response_time=0.1,
        last_check="2025-01-28T10:00:00Z",
        metadata={"test": True},
    )


@pytest.fixture
def mock_fal_provider(mock_image_result, mock_provider_health):
    """Mock FAL provider."""
    provider = MagicMock()
    provider.name = "fal"
    provider.generate_image = AsyncMock(return_value=mock_image_result)
    provider.upscale_image = AsyncMock(return_value=mock_image_result)
    provider.check_health = AsyncMock(return_value=mock_provider_health)
    provider.get_supported_models.return_value = ["fal-ai/flux/schnell"]
    provider.get_supported_styles.return_value = ["photorealistic", "cinematic"]
    return provider


@pytest.fixture
def mock_cms_response():
    """Mock PayloadCMS response."""
    return {
        "id": "test-media-id-123",
        "url": "https://test-cms.local/media/test-image.png",
        "filename": "test-image.png",
        "mimeType": "image/png",
        "filesize": 1024*1024,
        "width": 1024,
        "height": 1024,
        "createdAt": "2025-01-28T10:00:00Z",
        "updatedAt": "2025-01-28T10:00:00Z",
    }


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()