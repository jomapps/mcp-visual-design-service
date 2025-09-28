"""Test-only router to expose /api/v1/visual/styles without importing heavy services."""

from typing import Any, Dict
from fastapi import APIRouter

try:
    from ..templates import TemplateManager
except Exception:
    TemplateManager = None  # type: ignore

router = APIRouter(tags=["visual-test-stub"])


@router.get("/visual/styles", response_model=Dict[str, Any])
async def get_styles_stub() -> Dict[str, Any]:
    if TemplateManager is None:
        # Minimal fallback
        return {"styles": ["cinematic", "concept-art"], "details": {}}

    tm = TemplateManager()
    styles = tm.get_available_styles()
    details: Dict[str, Any] = {}
    for s in styles:
        t = tm.get_template(s)
        details[s] = {
            "name": getattr(t, "name", s),
            "description": getattr(t, "base_prompt", ""),
            "recommended_settings": getattr(t, "recommended_settings", {}),
        }
    return {"styles": styles, "details": details}


