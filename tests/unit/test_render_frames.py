import pytest

from src.routers.visual import _size_from_aspect_ratio, _build_prompt
from src.models.visual import (
    RenderStoryboardFramesRequest,
    StoryboardFrameInput,
    CharacterProfile,
    RenderSettings,
)


def test_size_from_aspect_ratio_known():
    assert _size_from_aspect_ratio("16:9") == (1280, 720)
    assert _size_from_aspect_ratio("4:3") == (1024, 768)
    assert _size_from_aspect_ratio("1:1") == (1024, 1024)


def test_size_from_aspect_ratio_custom_scales_within_limits():
    w, h = _size_from_aspect_ratio("21:9")
    assert w <= 1280 and h <= 720


def test_build_prompt_includes_all_parts():
    prompt = _build_prompt(
        desc="A hero stands on a cliff",
        cam="wide shot, low angle",
        light="golden hour",
        signatures=["Alice: red scarf", "Bob: blue jacket"],
    )
    assert "hero stands on a cliff" in prompt
    assert "Camera: wide shot, low angle" in prompt
    assert "Lighting: golden hour" in prompt
    assert "Character signatures:" in prompt


def test_request_model_defaults():
    req = RenderStoryboardFramesRequest(
        storyboard_frames=[
            StoryboardFrameInput(
                frame_id="SC_1_SH_1",
                description="Test scene",
            )
        ],
        character_profiles=[CharacterProfile(name="Alice", visual_signature="red scarf")],
    )
    assert req.render_settings.aspect_ratio == "16:9"
    assert req.render_settings.model == "fal-ai/flux-pro"

