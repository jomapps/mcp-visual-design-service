"""OpenRouter provider implementation for image generation."""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from pydantic import HttpUrl

from .base import (
    BaseProvider,
    ImageGenerationParams,
    ImageResult,
    ProviderError,
    ProviderHealth,
    ProviderStatus,
)


class OpenRouterProvider(BaseProvider):
    """OpenRouter image generation provider."""

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = kwargs.get("timeout", 60)
        
        # Supported models (image generation models available on OpenRouter)
        self._supported_models = [
            "black-forest-labs/flux-1.1-pro",
            "black-forest-labs/flux-1-schnell",
            "black-forest-labs/flux-1-dev",
            "ideogram-ai/ideogram-v2",
            "stability-ai/stable-diffusion-3.5-large",
            "stability-ai/stable-diffusion-3.5-large-turbo",
            "dataautogpt3/opendalle",
        ]
        
        # Supported styles
        self._supported_styles = [
            "photorealistic",
            "cinematic",
            "concept-art",
            "anime",
            "artistic",
            "digital-art",
        ]

    async def generate_image(self, params: ImageGenerationParams) -> ImageResult:
        """Generate image using OpenRouter API.

        Args:
            params: Image generation parameters

        Returns:
            Generated image result

        Raises:
            ProviderError: If generation fails
        """
        if not self.api_key:
            raise ProviderError(
                "OpenRouter API key is required", 
                provider="openrouter", 
                error_code="NO_API_KEY"
            )

        start_time = time.time()
        
        # Prepare request payload for OpenRouter image generation
        # Note: OpenRouter may use different API format depending on the model
        payload = {
            "model": params.model,
            "prompt": params.prompt,
            "max_tokens": 1024,  # For models that support this parameter
            "temperature": 0.7,
            "extra": {
                "image_generation": {
                    "width": params.width,
                    "height": params.height,
                    "steps": params.steps,
                    "guidance_scale": params.guidance_scale,
                    "num_images": 1,
                }
            }
        }
        
        if params.seed is not None:
            payload["extra"]["image_generation"]["seed"] = params.seed
            
        if params.negative_prompt:
            payload["extra"]["image_generation"]["negative_prompt"] = params.negative_prompt
            
        # Add additional parameters
        payload["extra"]["image_generation"].update(params.additional_params)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mcp-visual-design-service.local",
                    "X-Title": "MCP Visual Design Service",
                }
                
                # For image generation, we might need to use different endpoints
                # depending on the model. This is a simplified implementation.
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise ProviderError(
                        f"OpenRouter API error: {response.status_code}",
                        provider="openrouter",
                        error_code=str(response.status_code),
                        details=error_data,
                    )
                
                result_data = response.json()
                generation_time = time.time() - start_time
                
                # Extract image URL from response
                # Note: This is a simplified parsing - actual OpenRouter response
                # format may vary by model
                if "choices" not in result_data or not result_data["choices"]:
                    raise ProviderError(
                        "No choices returned from OpenRouter API",
                        provider="openrouter",
                        error_code="NO_CHOICES",
                    )
                
                choice = result_data["choices"][0]
                message_content = choice.get("message", {}).get("content", "")
                
                # For actual implementation, you'd parse the image URL from the response
                # This is a placeholder implementation
                image_url = self._extract_image_url_from_response(message_content)
                
                if not image_url:
                    raise ProviderError(
                        "No image URL found in OpenRouter response",
                        provider="openrouter",
                        error_code="NO_IMAGE_URL",
                    )
                
                return ImageResult(
                    url=HttpUrl(image_url),
                    width=params.width,
                    height=params.height,
                    file_size=None,  # OpenRouter may not provide file size
                    format="png",
                    seed=params.seed,
                    model=params.model,
                    provider="openrouter",
                    generation_time=generation_time,
                    metadata={
                        "prompt": params.prompt,
                        "steps": params.steps,
                        "guidance_scale": params.guidance_scale,
                        "usage": result_data.get("usage", {}),
                        "model_used": result_data.get("model"),
                    },
                )
                
        except httpx.TimeoutException:
            raise ProviderError(
                "OpenRouter API request timeout",
                provider="openrouter",
                error_code="TIMEOUT",
            )
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"OpenRouter API HTTP error: {e.response.status_code}",
                provider="openrouter",
                error_code=str(e.response.status_code),
            )
        except Exception as e:
            raise ProviderError(
                f"Unexpected OpenRouter API error: {str(e)}",
                provider="openrouter",
                error_code="UNEXPECTED",
            )

    def _extract_image_url_from_response(self, content: str) -> Optional[str]:
        """Extract image URL from OpenRouter response content.
        
        This is a placeholder implementation. The actual extraction logic
        would depend on how OpenRouter formats image generation responses.
        
        Args:
            content: Response content from OpenRouter
            
        Returns:
            Extracted image URL or None
        """
        # In a real implementation, you'd parse the content to extract the image URL
        # For now, return a placeholder URL for testing
        if "http" in content:
            # Simple URL extraction - improve this for production
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
            return urls[0] if urls else None
        return None

    async def upscale_image(
        self, image_url: str, factor: int = 2, **kwargs: Any
    ) -> ImageResult:
        """Upscale image using OpenRouter models.

        Args:
            image_url: URL of image to upscale
            factor: Upscaling factor
            **kwargs: Additional parameters

        Returns:
            Upscaled image result

        Raises:
            ProviderError: If upscaling fails
        """
        # OpenRouter doesn't have dedicated upscaling models in the same way as FAL
        # This would need to be implemented using image-to-image models or
        # specialized upscaling services available through OpenRouter
        raise ProviderError(
            "Image upscaling not yet implemented for OpenRouter provider",
            provider="openrouter",
            error_code="NOT_IMPLEMENTED",
        )

    async def check_health(self) -> ProviderHealth:
        """Check OpenRouter API health.

        Returns:
            Provider health status
        """
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                # Check models endpoint
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers,
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = len(models_data.get("data", []))
                    
                    return ProviderHealth(
                        status=ProviderStatus.HEALTHY,
                        message="OpenRouter API is accessible",
                        response_time=response_time,
                        last_check=datetime.utcnow().isoformat(),
                        metadata={
                            "has_api_key": bool(self.api_key),
                            "available_models": available_models,
                        },
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.DEGRADED,
                        message=f"OpenRouter API returned status {response.status_code}",
                        response_time=response_time,
                        last_check=datetime.utcnow().isoformat(),
                        metadata={"status_code": response.status_code},
                    )
                    
        except Exception as e:
            return ProviderHealth(
                status=ProviderStatus.UNHEALTHY,
                message=f"OpenRouter API health check failed: {str(e)}",
                response_time=None,
                last_check=datetime.utcnow().isoformat(),
                metadata={"error": str(e)},
            )

    def get_supported_models(self) -> list[str]:
        """Get supported OpenRouter models.

        Returns:
            List of supported model names
        """
        return self._supported_models.copy()

    def get_supported_styles(self) -> list[str]:
        """Get supported styles.

        Returns:
            List of supported style names
        """
        return self._supported_styles.copy()