"""Visual generation data models."""

from typing import Any, Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class VisualType(str, Enum):
    """Types of visual content."""

    STORYBOARD = "storyboard"
    CONCEPT = "concept"
    UPSCALE = "upscale"


class GenerationStatus(str, Enum):
    """Generation status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Scene(BaseModel):
    """Scene description for storyboard generation."""

    description: str = Field(..., description="Scene description")
    duration: Optional[float] = Field(None, description="Scene duration in seconds")
    mood: Optional[str] = Field(None, description="Scene mood or tone")
    camera_angle: Optional[str] = Field(None, description="Camera angle or shot type")
    lighting: Optional[str] = Field(None, description="Lighting description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class VisualAsset(BaseModel):
    """Generated visual asset."""

    id: str = Field(..., description="Asset ID")
    url: HttpUrl = Field(..., description="Asset URL")
    type: VisualType = Field(..., description="Asset type")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    provider: str = Field(..., description="Generation provider")
    model: str = Field(..., description="AI model used")
    prompt: str = Field(..., description="Generation prompt")
    generation_params: Dict[str, Any] = Field(default_factory=dict, description="Generation parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StoryboardGenerationRequest(BaseModel):
    """Request for storyboard generation."""

    project_id: str = Field(..., description="Project ID")
    scenes: List[Scene] = Field(..., description="List of scenes to generate")
    style_preset: str = Field(default="cinematic", description="Visual style preset")
    seed: Optional[int] = Field(None, description="Random seed for consistent results")
    aspect_ratio: str = Field(default="16:9", description="Aspect ratio")
    quality: str = Field(default="standard", description="Generation quality")
    provider_preference: Optional[str] = Field(None, description="Preferred provider")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class StoryboardGenerationResponse(BaseModel):
    """Response for storyboard generation."""

    generation_id: str = Field(..., description="Generation ID")
    project_id: str = Field(..., description="Project ID")
    status: GenerationStatus = Field(..., description="Generation status")
    assets: List[VisualAsset] = Field(default_factory=list, description="Generated assets")
    progress: float = Field(default=0.0, description="Generation progress (0.0-1.0)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    total_scenes: int = Field(..., description="Total number of scenes")
    completed_scenes: int = Field(default=0, description="Number of completed scenes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConceptGenerationRequest(BaseModel):
    """Request for concept art generation."""

    prompt: str = Field(..., description="Concept description")
    project_id: Optional[str] = Field(None, description="Project ID")
    reference_images: List[HttpUrl] = Field(default_factory=list, description="Reference image URLs")
    style_preset: str = Field(default="concept-art", description="Visual style preset")
    variations: int = Field(default=1, description="Number of variations to generate")
    aspect_ratio: str = Field(default="16:9", description="Aspect ratio")
    quality: str = Field(default="standard", description="Generation quality")
    provider_preference: Optional[str] = Field(None, description="Preferred provider")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConceptGenerationResponse(BaseModel):
    """Response for concept art generation."""

    generation_id: str = Field(..., description="Generation ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    status: GenerationStatus = Field(..., description="Generation status")
    assets: List[VisualAsset] = Field(default_factory=list, description="Generated assets")
    progress: float = Field(default=0.0, description="Generation progress (0.0-1.0)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpscaleRequest(BaseModel):
    """Request for image upscaling."""

    media_id: str = Field(..., description="Media asset ID to upscale")
    factor: int = Field(default=2, description="Upscaling factor (2x, 4x, etc.)")
    project_id: Optional[str] = Field(None, description="Project ID")
    quality: str = Field(default="standard", description="Upscaling quality")
    provider_preference: Optional[str] = Field(None, description="Preferred provider")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpscaleResponse(BaseModel):
    """Response for image upscaling."""

    generation_id: str = Field(..., description="Generation ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    status: GenerationStatus = Field(..., description="Generation status")
    original_asset_id: str = Field(..., description="Original asset ID")
    upscaled_asset: Optional[VisualAsset] = Field(None, description="Upscaled asset")
    progress: float = Field(default=0.0, description="Upscaling progress (0.0-1.0)")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")