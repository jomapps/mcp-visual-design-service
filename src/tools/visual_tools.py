"""MCP tools for visual generation workflows."""

import logging
from typing import Any, Dict, List, Optional

from ..models import (
    ConceptGenerationRequest,
    ConceptGenerationResponse,
    Scene,
    StoryboardGenerationRequest,
    StoryboardGenerationResponse,
    UpscaleRequest,
    UpscaleResponse,
)
from ..services import AssetService, ProviderFactory, VisualService
from ..config import settings

logger = logging.getLogger(__name__)


class VisualTools:
    """MCP tools for visual generation."""

    def __init__(self) -> None:
        """Initialize visual tools."""
        self.provider_factory = ProviderFactory(settings)
        self.asset_service = AssetService(settings)
        self.visual_service = VisualService(
            self.provider_factory, self.asset_service, settings
        )

    async def generate_storyboard(
        self,
        project_id: str,
        scenes: List[Dict[str, Any]],
        style_preset: str = "cinematic",
        seed: Optional[int] = None,
        aspect_ratio: str = "16:9",
        quality: str = "standard",
        provider_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate storyboard frames for scenes.

        This MCP tool generates visual storyboard frames from scene descriptions,
        applies style templates, and uploads results to PayloadCMS.

        Args:
            project_id: Project ID to associate with generated assets
            scenes: List of scene dictionaries with description, mood, etc.
            style_preset: Visual style preset (cinematic, concept-art, etc.)
            seed: Optional random seed for consistent results
            aspect_ratio: Image aspect ratio (16:9, 4:3, 1:1, etc.)
            quality: Generation quality (standard, high)
            provider_preference: Preferred image generation provider

        Returns:
            Dictionary with generation results and asset references
        """
        try:
            logger.info(f"MCP: Generating storyboard for project {project_id}")
            
            # Convert scene dictionaries to Scene objects
            scene_objects = []
            for scene_dict in scenes:
                scene = Scene(
                    description=scene_dict.get("description", ""),
                    duration=scene_dict.get("duration"),
                    mood=scene_dict.get("mood"),
                    camera_angle=scene_dict.get("camera_angle"),
                    lighting=scene_dict.get("lighting"),
                    metadata=scene_dict.get("metadata", {}),
                )
                scene_objects.append(scene)

            # Create storyboard generation request
            request = StoryboardGenerationRequest(
                project_id=project_id,
                scenes=scene_objects,
                style_preset=style_preset,
                seed=seed,
                aspect_ratio=aspect_ratio,
                quality=quality,
                provider_preference=provider_preference,
            )

            # Generate storyboard
            response = await self.visual_service.generate_storyboard(request)

            # Convert to MCP-friendly format
            return {
                "success": response.status == "completed",
                "generation_id": response.generation_id,
                "project_id": response.project_id,
                "status": response.status,
                "progress": response.progress,
                "total_scenes": response.total_scenes,
                "completed_scenes": response.completed_scenes,
                "assets": [
                    {
                        "id": asset.id,
                        "url": str(asset.url),
                        "type": asset.type,
                        "width": asset.width,
                        "height": asset.height,
                        "provider": asset.provider,
                        "model": asset.model,
                        "prompt": asset.prompt,
                    }
                    for asset in response.assets
                ],
                "error_message": response.error_message,
            }

        except Exception as e:
            logger.error(f"MCP storyboard generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_id": None,
                "project_id": project_id,
                "assets": [],
            }

    async def generate_concepts(
        self,
        prompt: str,
        project_id: Optional[str] = None,
        reference_images: Optional[List[str]] = None,
        style_preset: str = "concept-art",
        variations: int = 1,
        aspect_ratio: str = "16:9",
        quality: str = "standard",
        provider_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate concept art variations.

        This MCP tool generates concept art variations from a text description,
        optionally using reference images and style templates.

        Args:
            prompt: Text description for concept generation
            project_id: Optional project ID to associate with
            reference_images: Optional list of reference image URLs
            style_preset: Visual style preset
            variations: Number of variations to generate
            aspect_ratio: Image aspect ratio
            quality: Generation quality
            provider_preference: Preferred image generation provider

        Returns:
            Dictionary with generation results and asset references
        """
        try:
            logger.info(f"MCP: Generating concept art: {prompt[:50]}...")
            
            # Convert reference images to HttpUrl objects if provided
            reference_urls = []
            if reference_images:
                from pydantic import HttpUrl
                reference_urls = [HttpUrl(url) for url in reference_images]

            # Create concept generation request
            request = ConceptGenerationRequest(
                prompt=prompt,
                project_id=project_id,
                reference_images=reference_urls,
                style_preset=style_preset,
                variations=variations,
                aspect_ratio=aspect_ratio,
                quality=quality,
                provider_preference=provider_preference,
            )

            # Generate concepts
            response = await self.visual_service.generate_concept(request)

            # Convert to MCP-friendly format
            return {
                "success": response.status == "completed",
                "generation_id": response.generation_id,
                "project_id": response.project_id,
                "status": response.status,
                "progress": response.progress,
                "assets": [
                    {
                        "id": asset.id,
                        "url": str(asset.url),
                        "type": asset.type,
                        "width": asset.width,
                        "height": asset.height,
                        "provider": asset.provider,
                        "model": asset.model,
                        "prompt": asset.prompt,
                    }
                    for asset in response.assets
                ],
                "error_message": response.error_message,
            }

        except Exception as e:
            logger.error(f"MCP concept generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_id": None,
                "project_id": project_id,
                "assets": [],
            }

    async def upscale_image(
        self,
        media_id: str,
        factor: int = 2,
        project_id: Optional[str] = None,
        quality: str = "standard",
        provider_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upscale an existing image.

        This MCP tool upscales an existing image from PayloadCMS by the specified factor.

        Args:
            media_id: ID of the media asset to upscale
            factor: Upscaling factor (2x, 4x, etc.)
            project_id: Optional project ID to associate with
            quality: Upscaling quality
            provider_preference: Preferred upscaling provider

        Returns:
            Dictionary with upscaling results and asset reference
        """
        try:
            logger.info(f"MCP: Upscaling image {media_id} by {factor}x")
            
            # Create upscale request
            request = UpscaleRequest(
                media_id=media_id,
                factor=factor,
                project_id=project_id,
                quality=quality,
                provider_preference=provider_preference,
            )

            # Upscale image
            response = await self.visual_service.upscale_image(request)

            # Convert to MCP-friendly format
            result = {
                "success": response.status == "completed",
                "generation_id": response.generation_id,
                "project_id": response.project_id,
                "status": response.status,
                "progress": response.progress,
                "original_asset_id": response.original_asset_id,
                "error_message": response.error_message,
            }

            if response.upscaled_asset:
                result["upscaled_asset"] = {
                    "id": response.upscaled_asset.id,
                    "url": str(response.upscaled_asset.url),
                    "type": response.upscaled_asset.type,
                    "width": response.upscaled_asset.width,
                    "height": response.upscaled_asset.height,
                    "provider": response.upscaled_asset.provider,
                    "model": response.upscaled_asset.model,
                }
            else:
                result["upscaled_asset"] = None

            return result

        except Exception as e:
            logger.error(f"MCP image upscaling failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "generation_id": None,
                "project_id": project_id,
                "original_asset_id": media_id,
                "upscaled_asset": None,
            }

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the visual design service.

        This MCP tool checks the health of image generation providers and
        PayloadCMS connectivity.

        Returns:
            Dictionary with health status information
        """
        try:
            # Check provider health
            provider_health = await self.provider_factory.health_check()
            
            # Check PayloadCMS connectivity
            cms_healthy = await self.asset_service.check_connection()
            
            # Get available capabilities
            available_providers = self.provider_factory.get_available_providers()
            supported_models = self.provider_factory.get_supported_models()
            supported_styles = self.provider_factory.get_supported_styles()
            
            return {
                "success": True,
                "service": "mcp-visual-design-service",
                "version": "0.1.0",
                "providers": {
                    "available": available_providers,
                    "health": provider_health,
                },
                "payloadcms": {
                    "connected": cms_healthy,
                },
                "capabilities": {
                    "supported_models": supported_models,
                    "supported_styles": supported_styles,
                    "operations": ["storyboard", "concept", "upscale"],
                },
            }
            
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": "mcp-visual-design-service",
                "version": "0.1.0",
            }


# Global instance for MCP tool registration
visual_tools = VisualTools()