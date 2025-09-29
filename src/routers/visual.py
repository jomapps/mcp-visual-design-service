"""Visual generation API endpoints."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from ..models import (
    ConceptGenerationRequest,
    ConceptGenerationResponse,
    StoryboardGenerationRequest,
    StoryboardGenerationResponse,
    UpscaleRequest,
    UpscaleResponse,
)
from ..services.asset_service import AssetService
from ..services.provider_factory import ProviderFactory
from ..services.visual_service import VisualService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["visual"])


def get_visual_service(request: Request) -> VisualService:
    """Get visual service from app state."""
    provider_factory = request.app.state.provider_factory
    asset_service = AssetService(request.app.state.provider_factory.settings)
    return VisualService(provider_factory, asset_service, provider_factory.settings)


@router.post(
    "/visual/storyboard",
    response_model=StoryboardGenerationResponse,
    status_code=HTTP_200_OK,
    summary="Generate storyboard frames",
    description="Generate visual storyboard frames from scene descriptions",
)
async def generate_storyboard(
    request: StoryboardGenerationRequest,
    visual_service: VisualService = Depends(get_visual_service),
) -> StoryboardGenerationResponse:
    """Generate storyboard frames for scenes.

    Args:
        request: Storyboard generation request
        visual_service: Visual service instance

    Returns:
        Storyboard generation response

    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info(f"Generating storyboard for project {request.project_id}")
        response = await visual_service.generate_storyboard(request)
        return response

    except ValueError as e:
        logger.error(f"Invalid storyboard request: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Storyboard generation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during storyboard generation",
        )


@router.post(
    "/visual/concept",
    response_model=ConceptGenerationResponse,
    status_code=HTTP_200_OK,
    summary="Generate concept art",
    description="Generate concept art variations from description",
)
async def generate_concept(
    request: ConceptGenerationRequest,
    visual_service: VisualService = Depends(get_visual_service),
) -> ConceptGenerationResponse:
    """Generate concept art.

    Args:
        request: Concept generation request
        visual_service: Visual service instance

    Returns:
        Concept generation response

    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info(f"Generating concept art: {request.prompt[:50]}...")
        response = await visual_service.generate_concept(request)
        return response

    except ValueError as e:
        logger.error(f"Invalid concept request: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Concept generation failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during concept generation",
        )


@router.post(
    "/visual/upscale",
    response_model=UpscaleResponse,
    status_code=HTTP_200_OK,
    summary="Upscale image",
    description="Upscale an existing image by specified factor",
)
async def upscale_image(
    request: UpscaleRequest,
    visual_service: VisualService = Depends(get_visual_service),
) -> UpscaleResponse:
    """Upscale an existing image.

    Args:
        request: Upscale request
        visual_service: Visual service instance

    Returns:
        Upscale response

    Raises:
        HTTPException: If upscaling fails
    """
    try:
        logger.info(f"Upscaling image {request.media_id} by {request.factor}x")
        response = await visual_service.upscale_image(request)
        return response

    except ValueError as e:
        logger.error(f"Invalid upscale request: {e}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Image upscaling failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during image upscaling",
        )


@router.get(
    "/visual/providers",
    response_model=Dict[str, Any],
    status_code=HTTP_200_OK,
    summary="Get available providers",
    description="Get list of available image generation providers and their capabilities",
)
async def get_providers(
    request: Request,
) -> Dict[str, Any]:
    """Get available providers and their capabilities.

    Args:
        request: FastAPI request

    Returns:
        Dictionary with provider information
    """
    try:
        provider_factory: ProviderFactory = request.app.state.provider_factory

        return {
            "providers": provider_factory.get_available_providers(),
            "models": {
                provider: provider_factory.get_supported_models(provider)
                for provider in provider_factory.get_available_providers()
            },
            "styles": provider_factory.get_supported_styles(),
            "health": await provider_factory.health_check(),
        }

    except Exception as e:
        logger.error(f"Failed to get provider info: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve provider information",
        )


@router.get(
    "/visual/styles",
    response_model=Dict[str, Any],
    status_code=HTTP_200_OK,
    summary="Get available styles",
    description="Get list of available visual style presets and templates",
)
async def get_styles() -> Dict[str, Any]:
    """Get available style presets.

    Returns:
        Dictionary with style information
    """
    from ..templates import TemplateManager

    try:
        template_manager = TemplateManager()
        available_styles = template_manager.get_available_styles()

        # Get template details for each style
        style_details = {}
        for style in available_styles:
            template = template_manager.get_template(style)
            style_details[style] = {
                "name": template.name,
                "description": template.base_prompt,
                "recommended_settings": template.recommended_settings,
            }

        return {
            "styles": available_styles,
            "details": style_details,
        }

    except Exception as e:
        logger.error(f"Failed to get style info: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve style information",
        )


# --- Image Generation (Storyboard Frames) Endpoint ---
from fastapi import Request
from ..models.visual import (
    RenderStoryboardFramesRequest,
    RenderStoryboardFramesResponse,
    RenderedFrame,
    FailedFrame,
)
from ..providers.base import ImageGenerationParams, ProviderError


def _size_from_aspect_ratio(ratio: str) -> tuple[int, int]:
    mapping = {
        "16:9": (1280, 720),
        "4:3": (1024, 768),
        "1:1": (1024, 1024),
    }
    if ratio in mapping:
        return mapping[ratio]
    try:
        w, h = ratio.split(":")
        w_i, h_i = int(w), int(h)
        # scale to max width=1280 while preserving ratio
        max_w = 1280
        scaled_h = int(max_w * h_i / w_i)
        if scaled_h > 720:
            # fallback to max height 720
            max_h = 720
            scaled_w = int(max_h * w_i / h_i)
            return (scaled_w, max_h)
        return (max_w, scaled_h)
    except Exception:
        return (1280, 720)


def _build_prompt(desc: str, cam: str | None, light: str | None, signatures: list[str]) -> str:
    parts = [desc.strip()]
    if cam:
        parts.append(f"Camera: {cam.strip()}.")
    if light:
        parts.append(f"Lighting: {light.strip()}.")
    if signatures:
        parts.append("Character signatures: " + "; ".join(s.strip() for s in signatures))
    return " ".join(p for p in parts if p)


@router.post(
    "/visual/render-frames",
    response_model=RenderStoryboardFramesResponse,
    status_code=HTTP_200_OK,
    summary="Render storyboard frames (key frames)",
    description="Generate images per storyboard frame using FAL.ai (MVP)",
)
async def render_storyboard_frames(
    payload: RenderStoryboardFramesRequest,
    request: Request,
) -> RenderStoryboardFramesResponse:
    try:
        provider_factory: ProviderFactory = request.app.state.provider_factory
        # Clarification: only fal.ai for MVP
        provider = provider_factory.get_provider("fal")

        signatures = [cp.visual_signature for cp in payload.character_profiles]
        width, height = _size_from_aspect_ratio(payload.render_settings.aspect_ratio)

        generated: list[RenderedFrame] = []
        failed: list[FailedFrame] = []

        negative_prompt_default = "blurry, low quality, distorted, extra limbs, watermark"

        for frame in payload.storyboard_frames:
            prompt = _build_prompt(
                frame.description,
                frame.camera_notes,
                frame.lighting_mood,
                signatures,
            )

            params = ImageGenerationParams(
                prompt=prompt,
                model=payload.render_settings.model or "fal-ai/flux-pro",
                width=width,
                height=height,
                seed=frame.prompt_seed if frame.prompt_seed is not None else payload.render_settings.seed,
                steps=payload.render_settings.steps,
                guidance_scale=payload.render_settings.guidance_scale,
                negative_prompt=negative_prompt_default,
                aspect_ratio=payload.render_settings.aspect_ratio,
            )

            try:
                result = await provider.generate_image(params)
                generated.append(
                    RenderedFrame(
                        frame_id=frame.frame_id,
                        image_url=str(result.url),
                        negative_prompts=[negative_prompt_default],
                        provider_metadata={
                            "seed": result.seed,
                            "model": result.model,
                            "provider": result.provider,
                            "generation_time_ms": int(result.generation_time * 1000),
                        },
                        quality_score=None,  # Optional scoring can be plugged later
                    )
                )
            except ProviderError as e:
                failed.append(FailedFrame(frame_id=frame.frame_id, error=e.error_code or "provider_error"))
                # Clarification: stop on first failure, no retries/fallbacks
                break
            except Exception as e:
                failed.append(FailedFrame(frame_id=frame.frame_id, error="unexpected_error"))
                break

        return RenderStoryboardFramesResponse(generated_frames=generated, failed_frames=failed)

    except ValueError as e:
        logger.error(f"Invalid render request: {e}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        logger.error(f"Render frames failed: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during frame rendering",
        )
