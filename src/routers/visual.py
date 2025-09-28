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
from ..services import AssetService, ProviderFactory, VisualService

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