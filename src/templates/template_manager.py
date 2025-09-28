"""Template manager for prompt templates."""

from typing import Any, Dict, Optional
from enum import Enum

from pydantic import BaseModel


class StylePreset(str, Enum):
    """Available style presets."""
    
    CINEMATIC = "cinematic"
    CONCEPT_ART = "concept-art"
    PHOTOREALISTIC = "photorealistic"
    ANIME = "anime"
    ARTISTIC = "artistic"
    STORYBOARD = "storyboard"


class StyleTemplate(BaseModel):
    """Template for a specific visual style."""
    
    name: str
    base_prompt: str
    style_modifiers: list[str]
    negative_prompt: Optional[str] = None
    recommended_settings: Dict[str, Any]


class TemplateManager:
    """Manager for prompt templates."""
    
    def __init__(self) -> None:
        """Initialize template manager."""
        self._templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, StyleTemplate]:
        """Initialize built-in style templates."""
        return {
            StylePreset.CINEMATIC: StyleTemplate(
                name="Cinematic",
                base_prompt="A cinematic {scene_description}, professional film quality, dramatic lighting",
                style_modifiers=[
                    "35mm film",
                    "cinematic composition", 
                    "professional cinematography",
                    "dramatic lighting",
                    "film grain",
                    "depth of field",
                ],
                negative_prompt="amateur, low quality, blurry, overexposed, cartoon, anime",
                recommended_settings={
                    "steps": 30,
                    "guidance_scale": 7.5,
                    "aspect_ratio": "16:9",
                },
            ),
            
            StylePreset.CONCEPT_ART: StyleTemplate(
                name="Concept Art",
                base_prompt="Concept art of {scene_description}, digital painting, detailed illustration",
                style_modifiers=[
                    "concept art",
                    "digital painting",
                    "detailed illustration",
                    "matte painting",
                    "environment design",
                    "professional concept art",
                ],
                negative_prompt="photograph, realistic, amateur, sketch, low quality",
                recommended_settings={
                    "steps": 25,
                    "guidance_scale": 8.0,
                    "aspect_ratio": "16:9",
                },
            ),
            
            StylePreset.PHOTOREALISTIC: StyleTemplate(
                name="Photorealistic", 
                base_prompt="Photorealistic {scene_description}, high quality photography, realistic lighting",
                style_modifiers=[
                    "photorealistic",
                    "high quality photography",
                    "realistic lighting",
                    "professional photography",
                    "detailed",
                    "sharp focus",
                ],
                negative_prompt="cartoon, anime, painting, illustration, low quality, blurry",
                recommended_settings={
                    "steps": 35,
                    "guidance_scale": 7.0,
                    "aspect_ratio": "3:2",
                },
            ),
            
            StylePreset.ANIME: StyleTemplate(
                name="Anime",
                base_prompt="Anime style {scene_description}, high quality anime art, detailed animation style",
                style_modifiers=[
                    "anime style",
                    "high quality anime",
                    "detailed animation",
                    "manga style",
                    "cel shading",
                    "vibrant colors",
                ],
                negative_prompt="realistic, photograph, western cartoon, low quality, blurry",
                recommended_settings={
                    "steps": 25,
                    "guidance_scale": 8.5,
                    "aspect_ratio": "16:9",
                },
            ),
            
            StylePreset.ARTISTIC: StyleTemplate(
                name="Artistic",
                base_prompt="Artistic interpretation of {scene_description}, creative style, expressive artwork",
                style_modifiers=[
                    "artistic",
                    "creative style",
                    "expressive artwork",
                    "unique style",
                    "artistic vision",
                    "creative composition",
                ],
                negative_prompt="boring, generic, low quality, amateur",
                recommended_settings={
                    "steps": 28,
                    "guidance_scale": 7.5,
                    "aspect_ratio": "1:1",
                },
            ),
            
            StylePreset.STORYBOARD: StyleTemplate(
                name="Storyboard",
                base_prompt="Storyboard frame of {scene_description}, professional storyboard art, clear composition",
                style_modifiers=[
                    "storyboard",
                    "professional storyboard art",
                    "clear composition",
                    "film pre-production",
                    "sketch style",
                    "black and white",
                ],
                negative_prompt="colorful, detailed painting, photorealistic, low quality",
                recommended_settings={
                    "steps": 20,
                    "guidance_scale": 6.5,
                    "aspect_ratio": "16:9",
                },
            ),
        }
    
    def get_template(self, style_preset: str) -> StyleTemplate:
        """Get template for a style preset.
        
        Args:
            style_preset: Style preset name
            
        Returns:
            Style template
            
        Raises:
            ValueError: If style preset not found
        """
        if style_preset not in self._templates:
            raise ValueError(f"Unknown style preset: {style_preset}")
        
        return self._templates[style_preset]
    
    def apply_template(
        self,
        style_preset: str,
        scene_description: str,
        additional_context: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Apply template to generate final prompt.
        
        Args:
            style_preset: Style preset name
            scene_description: Scene description to incorporate
            additional_context: Additional context variables
            
        Returns:
            Dictionary with prompt and settings
        """
        template = self.get_template(style_preset)
        
        # Build context for template substitution
        context = {
            "scene_description": scene_description,
            **(additional_context or {}),
        }
        
        # Apply base prompt template
        final_prompt = template.base_prompt.format(**context)
        
        # Add style modifiers
        if template.style_modifiers:
            style_text = ", ".join(template.style_modifiers)
            final_prompt = f"{final_prompt}, {style_text}"
        
        return {
            "prompt": final_prompt,
            "negative_prompt": template.negative_prompt,
            "settings": template.recommended_settings,
            "style_name": template.name,
        }
    
    def get_available_styles(self) -> list[str]:
        """Get list of available style presets.
        
        Returns:
            List of style preset names
        """
        return list(self._templates.keys())
    
    def add_custom_template(
        self,
        name: str,
        template: StyleTemplate,
    ) -> None:
        """Add a custom template.
        
        Args:
            name: Template name
            template: Style template
        """
        self._templates[name] = template