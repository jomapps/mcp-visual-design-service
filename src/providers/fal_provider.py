"""FAL AI provider implementation."""

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


class FalProvider(BaseProvider):
    """FAL AI image generation provider."""

    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize FAL provider.

        Args:
            api_key: FAL API key
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = "https://fal.run/"
        self.timeout = kwargs.get("timeout", 60)
        
        # Supported models
        self._supported_models = [
            "fal-ai/flux/schnell",
            "fal-ai/flux/dev",
            "fal-ai/flux-pro",
            "fal-ai/flux-realism",
            "fal-ai/aura-flow",
        ]
        
        # Supported styles
        self._supported_styles = [
            "photorealistic",
            "cinematic",
            "concept-art",
            "anime",
            "artistic",
            "realistic",
        ]

    async def generate_image(self, params: ImageGenerationParams) -> ImageResult:
        """Generate image using FAL API.

        Args:
            params: Image generation parameters

        Returns:
            Generated image result

        Raises:
            ProviderError: If generation fails
        """
        if not self.api_key:
            raise ProviderError(
                "FAL API key is required", provider="fal", error_code="NO_API_KEY"
            )

        start_time = time.time()
        
        # Prepare request payload
        payload = {
            "prompt": params.prompt,
            "image_size": {
                "width": params.width,
                "height": params.height,
            },
            "num_inference_steps": params.steps,
            "guidance_scale": params.guidance_scale,
            "num_images": 1,
            "enable_safety_checker": True,
            "format": "png",
        }
        
        if params.seed is not None:
            payload["seed"] = params.seed
            
        if params.negative_prompt:
            payload["negative_prompt"] = params.negative_prompt
            
        # Add model-specific parameters
        payload.update(params.additional_params)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Key {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                # Submit generation request
                response = await client.post(
                    f"{self.base_url}{params.model}",
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise ProviderError(
                        f"FAL API error: {response.status_code}",
                        provider="fal",
                        error_code=str(response.status_code),
                        details=error_data,
                    )
                
                result_data = response.json()
                
                # Extract image URL and metadata
                if "images" not in result_data or not result_data["images"]:
                    raise ProviderError(
                        "No images returned from FAL API",
                        provider="fal",
                        error_code="NO_IMAGES",
                    )
                
                image_data = result_data["images"][0]
                generation_time = time.time() - start_time
                
                return ImageResult(
                    url=HttpUrl(image_data["url"]),
                    width=image_data.get("width", params.width),
                    height=image_data.get("height", params.height),
                    file_size=image_data.get("file_size"),
                    format="png",
                    seed=result_data.get("seed", params.seed),
                    model=params.model,
                    provider="fal",
                    generation_time=generation_time,
                    metadata={
                        "prompt": params.prompt,
                        "steps": params.steps,
                        "guidance_scale": params.guidance_scale,
                        "fal_request_id": result_data.get("request_id"),
                        **result_data.get("timings", {}),
                    },
                )
                
        except httpx.TimeoutException:
            raise ProviderError(
                "FAL API request timeout",
                provider="fal",
                error_code="TIMEOUT",
            )
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"FAL API HTTP error: {e.response.status_code}",
                provider="fal",
                error_code=str(e.response.status_code),
            )
        except Exception as e:
            raise ProviderError(
                f"Unexpected FAL API error: {str(e)}",
                provider="fal",
                error_code="UNEXPECTED",
            )

    async def upscale_image(
        self, image_url: str, factor: int = 2, **kwargs: Any
    ) -> ImageResult:
        """Upscale image using FAL upscaling models.

        Args:
            image_url: URL of image to upscale
            factor: Upscaling factor
            **kwargs: Additional parameters

        Returns:
            Upscaled image result

        Raises:
            ProviderError: If upscaling fails
        """
        if not self.api_key:
            raise ProviderError(
                "FAL API key is required", provider="fal", error_code="NO_API_KEY"
            )

        start_time = time.time()
        
        # Choose appropriate upscaling model
        upscale_model = "fal-ai/clarity-upscaler"
        if factor >= 4:
            upscale_model = "fal-ai/esrgan"

        payload = {
            "image_url": image_url,
            "scale": factor,
            "format": "png",
        }
        
        payload.update(kwargs)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Key {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                response = await client.post(
                    f"{self.base_url}{upscale_model}",
                    json=payload,
                    headers=headers,
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise ProviderError(
                        f"FAL upscaling API error: {response.status_code}",
                        provider="fal",
                        error_code=str(response.status_code),
                        details=error_data,
                    )
                
                result_data = response.json()
                generation_time = time.time() - start_time
                
                return ImageResult(
                    url=HttpUrl(result_data["image"]["url"]),
                    width=result_data["image"].get("width", 0),
                    height=result_data["image"].get("height", 0),
                    file_size=result_data["image"].get("file_size"),
                    format="png",
                    seed=None,
                    model=upscale_model,
                    provider="fal",
                    generation_time=generation_time,
                    metadata={
                        "original_url": image_url,
                        "upscale_factor": factor,
                        "fal_request_id": result_data.get("request_id"),
                    },
                )
                
        except Exception as e:
            raise ProviderError(
                f"FAL upscaling error: {str(e)}",
                provider="fal",
                error_code="UPSCALE_FAILED",
            )

    async def check_health(self) -> ProviderHealth:
        """Check FAL API health.

        Returns:
            Provider health status
        """
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Test with a simple health check or model list request
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Key {self.api_key}"
                
                response = await client.get(
                    "https://fal.run/fal-ai/flux/schnell",  # Basic model endpoint
                    headers=headers,
                )
                
                response_time = time.time() - start_time
                
                if response.status_code in [200, 422]:  # 422 is expected for GET on generation endpoint
                    return ProviderHealth(
                        status=ProviderStatus.HEALTHY,
                        message="FAL API is accessible",
                        response_time=response_time,
                        last_check=datetime.utcnow().isoformat(),
                        metadata={"has_api_key": bool(self.api_key)},
                    )
                else:
                    return ProviderHealth(
                        status=ProviderStatus.DEGRADED,
                        message=f"FAL API returned status {response.status_code}",
                        response_time=response_time,
                        last_check=datetime.utcnow().isoformat(),
                        metadata={"status_code": response.status_code},
                    )
                    
        except Exception as e:
            return ProviderHealth(
                status=ProviderStatus.UNHEALTHY,
                message=f"FAL API health check failed: {str(e)}",
                response_time=None,
                last_check=datetime.utcnow().isoformat(),
                metadata={"error": str(e)},
            )

    def get_supported_models(self) -> list[str]:
        """Get supported FAL models.

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