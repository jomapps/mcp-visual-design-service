"""Main visual generation service."""

import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional

from ..config import Settings
from ..models import (
    ConceptGenerationRequest,
    ConceptGenerationResponse,
    GenerationStatus,
    Scene,
    StoryboardGenerationRequest,
    StoryboardGenerationResponse,
    UpscaleRequest,
    UpscaleResponse,
    VisualAsset,
    VisualType,
)
from ..providers import BaseProvider, ImageGenerationParams, ProviderError
from ..templates import TemplateManager
from .asset_service import AssetService
from .provider_factory import ProviderFactory

logger = logging.getLogger(__name__)


class VisualService:
    """Main service for visual generation workflows."""

    def __init__(
        self,
        provider_factory: ProviderFactory,
        asset_service: AssetService,
        settings: Settings,
    ) -> None:
        """Initialize visual service.

        Args:
            provider_factory: Provider factory for image generation
            asset_service: Asset service for PayloadCMS integration
            settings: Application settings
        """
        self.provider_factory = provider_factory
        self.asset_service = asset_service
        self.settings = settings
        self.template_manager = TemplateManager()

    async def generate_storyboard(
        self, request: StoryboardGenerationRequest
    ) -> StoryboardGenerationResponse:
        """Generate storyboard frames for scenes.

        Args:
            request: Storyboard generation request

        Returns:
            Storyboard generation response
        """
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting storyboard generation {generation_id} for project {request.project_id}")

        try:
            # Initialize response
            response = StoryboardGenerationResponse(
                generation_id=generation_id,
                project_id=request.project_id,
                status=GenerationStatus.PROCESSING,
                total_scenes=len(request.scenes),
                completed_scenes=0,
            )

            # Get provider
            provider = self.provider_factory.get_provider(request.provider_preference)

            # Process scenes in parallel with limited concurrency
            semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent generations
            tasks = [
                self._generate_scene_frame(
                    provider,
                    scene,
                    request,
                    generation_id,
                    scene_idx,
                    semaphore,
                )
                for scene_idx, scene in enumerate(request.scenes)
            ]

            # Wait for all generations to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Scene generation failed: {result}")
                    continue
                if result:
                    response.assets.append(result)
                    response.completed_scenes += 1

            # Update final status
            if response.completed_scenes == response.total_scenes:
                response.status = GenerationStatus.COMPLETED
                response.progress = 1.0
            elif response.completed_scenes > 0:
                response.status = GenerationStatus.COMPLETED
                response.progress = response.completed_scenes / response.total_scenes
            else:
                response.status = GenerationStatus.FAILED
                response.error_message = "Failed to generate any scenes"

            logger.info(
                f"Storyboard generation {generation_id} completed: "
                f"{response.completed_scenes}/{response.total_scenes} scenes"
            )

            return response

        except Exception as e:
            logger.error(f"Storyboard generation {generation_id} failed: {e}")
            return StoryboardGenerationResponse(
                generation_id=generation_id,
                project_id=request.project_id,
                status=GenerationStatus.FAILED,
                error_message=str(e),
                total_scenes=len(request.scenes),
            )

    async def _generate_scene_frame(
        self,
        provider: BaseProvider,
        scene: Scene,
        request: StoryboardGenerationRequest,
        generation_id: str,
        scene_idx: int,
        semaphore: asyncio.Semaphore,
    ) -> Optional[VisualAsset]:
        """Generate a single scene frame.

        Args:
            provider: Image generation provider
            scene: Scene to generate
            request: Original storyboard request
            generation_id: Generation ID
            scene_idx: Scene index
            semaphore: Semaphore for concurrency control

        Returns:
            Generated visual asset or None if failed
        """
        async with semaphore:
            try:
                # Apply prompt template
                template_result = self.template_manager.apply_template(
                    request.style_preset,
                    scene.description,
                    {
                        "mood": scene.mood or "neutral",
                        "camera_angle": scene.camera_angle or "medium shot",
                        "lighting": scene.lighting or "natural lighting",
                    },
                )

                # Parse aspect ratio
                width, height = self._parse_aspect_ratio(
                    request.aspect_ratio, base_size=1024
                )

                # Prepare generation parameters
                generation_params = ImageGenerationParams(
                    prompt=template_result["prompt"],
                    model=self._select_model(provider, request.quality),
                    width=width,
                    height=height,
                    seed=request.seed,
                    negative_prompt=template_result["negative_prompt"],
                    quality=request.quality,
                    aspect_ratio=request.aspect_ratio,
                    **template_result["settings"],
                )

                # Generate image
                logger.debug(f"Generating scene {scene_idx} with provider {provider.name}")
                image_result = await provider.generate_image(generation_params)

                # Upload to PayloadCMS
                filename = f"storyboard_{generation_id}_scene_{scene_idx:03d}.png"
                metadata = {
                    "type": VisualType.STORYBOARD.value,
                    "provider": provider.name,
                    "model": generation_params.model,
                    "scene_index": scene_idx,
                    "generation_id": generation_id,
                    "style_preset": request.style_preset,
                    "prompt": generation_params.prompt,
                    **scene.metadata,
                }

                cms_result = await self.asset_service.upload_image(
                    str(image_result.url),
                    filename,
                    request.project_id,
                    metadata,
                )

                # Create visual asset
                return VisualAsset(
                    id=cms_result["id"],
                    url=cms_result["url"],
                    type=VisualType.STORYBOARD,
                    width=image_result.width,
                    height=image_result.height,
                    file_size=image_result.file_size,
                    provider=provider.name,
                    model=generation_params.model,
                    prompt=generation_params.prompt,
                    generation_params=generation_params.dict(),
                    metadata=metadata,
                )

            except Exception as e:
                logger.error(f"Failed to generate scene {scene_idx}: {e}")
                return None

    async def generate_concept(
        self, request: ConceptGenerationRequest
    ) -> ConceptGenerationResponse:
        """Generate concept art.

        Args:
            request: Concept generation request

        Returns:
            Concept generation response
        """
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting concept generation {generation_id}")

        try:
            # Initialize response
            response = ConceptGenerationResponse(
                generation_id=generation_id,
                project_id=request.project_id,
                status=GenerationStatus.PROCESSING,
            )

            # Get provider
            provider = self.provider_factory.get_provider(request.provider_preference)

            # Generate variations
            tasks = [
                self._generate_concept_variation(
                    provider,
                    request,
                    generation_id,
                    variation_idx,
                )
                for variation_idx in range(request.variations)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Concept variation generation failed: {result}")
                    continue
                if result:
                    response.assets.append(result)

            # Update status
            if response.assets:
                response.status = GenerationStatus.COMPLETED
                response.progress = 1.0
            else:
                response.status = GenerationStatus.FAILED
                response.error_message = "Failed to generate any concept variations"

            return response

        except Exception as e:
            logger.error(f"Concept generation {generation_id} failed: {e}")
            return ConceptGenerationResponse(
                generation_id=generation_id,
                project_id=request.project_id,
                status=GenerationStatus.FAILED,
                error_message=str(e),
            )

    async def _generate_concept_variation(
        self,
        provider: BaseProvider,
        request: ConceptGenerationRequest,
        generation_id: str,
        variation_idx: int,
    ) -> Optional[VisualAsset]:
        """Generate a single concept variation.

        Args:
            provider: Image generation provider
            request: Concept generation request
            generation_id: Generation ID
            variation_idx: Variation index

        Returns:
            Generated visual asset or None if failed
        """
        try:
            # Apply prompt template
            template_result = self.template_manager.apply_template(
                request.style_preset,
                request.prompt,
            )

            # Parse aspect ratio
            width, height = self._parse_aspect_ratio(
                request.aspect_ratio, base_size=1024
            )

            # Prepare generation parameters
            generation_params = ImageGenerationParams(
                prompt=template_result["prompt"],
                model=self._select_model(provider, request.quality),
                width=width,
                height=height,
                negative_prompt=template_result["negative_prompt"],
                quality=request.quality,
                aspect_ratio=request.aspect_ratio,
                **template_result["settings"],
            )

            # Generate image
            image_result = await provider.generate_image(generation_params)

            # Upload to PayloadCMS
            filename = f"concept_{generation_id}_var_{variation_idx:02d}.png"
            metadata = {
                "type": VisualType.CONCEPT.value,
                "provider": provider.name,
                "model": generation_params.model,
                "variation_index": variation_idx,
                "generation_id": generation_id,
                "style_preset": request.style_preset,
                "prompt": generation_params.prompt,
            }

            cms_result = await self.asset_service.upload_image(
                str(image_result.url),
                filename,
                request.project_id,
                metadata,
            )

            return VisualAsset(
                id=cms_result["id"],
                url=cms_result["url"],
                type=VisualType.CONCEPT,
                width=image_result.width,
                height=image_result.height,
                file_size=image_result.file_size,
                provider=provider.name,
                model=generation_params.model,
                prompt=generation_params.prompt,
                generation_params=generation_params.dict(),
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Failed to generate concept variation {variation_idx}: {e}")
            return None

    async def upscale_image(self, request: UpscaleRequest) -> UpscaleResponse:
        """Upscale an existing image.

        Args:
            request: Upscale request

        Returns:
            Upscale response
        """
        generation_id = str(uuid.uuid4())
        logger.info(f"Starting upscale {generation_id} for media {request.media_id}")

        try:
            # Get original media
            original_media = await self.asset_service.get_media_by_id(request.media_id)
            if not original_media:
                return UpscaleResponse(
                    generation_id=generation_id,
                    project_id=request.project_id,
                    status=GenerationStatus.FAILED,
                    error_message=f"Media {request.media_id} not found",
                    original_asset_id=request.media_id,
                )

            # Get provider
            provider = self.provider_factory.get_provider(request.provider_preference)

            # Upscale image
            image_result = await provider.upscale_image(
                original_media["url"], request.factor
            )

            # Upload upscaled image
            filename = f"upscaled_{generation_id}_{request.factor}x.png"
            metadata = {
                "type": VisualType.UPSCALE.value,
                "provider": provider.name,
                "original_media_id": request.media_id,
                "upscale_factor": request.factor,
                "generation_id": generation_id,
            }

            cms_result = await self.asset_service.upload_image(
                str(image_result.url),
                filename,
                request.project_id,
                metadata,
            )

            upscaled_asset = VisualAsset(
                id=cms_result["id"],
                url=cms_result["url"],
                type=VisualType.UPSCALE,
                width=image_result.width,
                height=image_result.height,
                file_size=image_result.file_size,
                provider=provider.name,
                model=image_result.model,
                prompt=f"Upscale {request.factor}x",
                generation_params={"factor": request.factor},
                metadata=metadata,
            )

            return UpscaleResponse(
                generation_id=generation_id,
                project_id=request.project_id,
                status=GenerationStatus.COMPLETED,
                original_asset_id=request.media_id,
                upscaled_asset=upscaled_asset,
                progress=1.0,
            )

        except ProviderError as e:
            if e.error_code == "NOT_IMPLEMENTED":
                return UpscaleResponse(
                    generation_id=generation_id,
                    project_id=request.project_id,
                    status=GenerationStatus.FAILED,
                    error_message="Upscaling not supported by the selected provider",
                    original_asset_id=request.media_id,
                )
            else:
                raise
        except Exception as e:
            logger.error(f"Upscale {generation_id} failed: {e}")
            return UpscaleResponse(
                generation_id=generation_id,
                project_id=request.project_id,
                status=GenerationStatus.FAILED,
                error_message=str(e),
                original_asset_id=request.media_id,
            )

    def _parse_aspect_ratio(self, aspect_ratio: str, base_size: int = 1024) -> tuple[int, int]:
        """Parse aspect ratio string to width and height.

        Args:
            aspect_ratio: Aspect ratio string (e.g., "16:9", "1:1")
            base_size: Base size for calculations

        Returns:
            Tuple of (width, height)
        """
        try:
            width_ratio, height_ratio = map(int, aspect_ratio.split(":"))
            
            # Calculate dimensions maintaining aspect ratio
            if width_ratio >= height_ratio:
                width = base_size
                height = int(base_size * height_ratio / width_ratio)
            else:
                height = base_size
                width = int(base_size * width_ratio / height_ratio)
            
            # Ensure dimensions are multiples of 8 (common requirement)
            width = (width // 8) * 8
            height = (height // 8) * 8
            
            return width, height
            
        except (ValueError, ZeroDivisionError):
            # Default to square if parsing fails
            return base_size, base_size

    def _select_model(self, provider: BaseProvider, quality: str) -> str:
        """Select appropriate model based on provider and quality.

        Args:
            provider: Image generation provider
            quality: Desired quality level

        Returns:
            Model name
        """
        models = provider.get_supported_models()
        if not models:
            # Fallback based on provider type
            if provider.name == "fal":
                return self.settings.fal_text_to_image_model
            elif provider.name == "openrouter":
                return self.settings.openrouter_default_model
            else:
                return "default"
        
        # Select model based on quality
        if quality == "high" and len(models) > 1:
            return models[1]  # Second model for high quality
        else:
            return models[0]  # First model for standard quality