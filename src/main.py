"""Main FastAPI application for MCP Visual Design Service."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .routers.spec_requests import router as spec_router
from .routers.styles_stub import router as styles_stub_router
from .services.provider_factory import ProviderFactory

from .routers.visual import router as visual_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    service: str
    version: str
    providers: dict[str, str]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    logger.info("Starting MCP Visual Design Service")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Service will run on {settings.host}:{settings.port}")

    # Initialize provider factory
    provider_factory = ProviderFactory(settings)
    app.state.provider_factory = provider_factory

    # Test provider connections (skip in test environment)
    if settings.environment != "test":
        providers_status = await provider_factory.health_check()
        logger.info(f"Provider status: {providers_status}")

    yield

    logger.info("Shutting down MCP Visual Design Service")


app = FastAPI(
    title="MCP Visual Design Service",
    description="AI-powered visual design and asset generation service for movie production",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(visual_router, prefix="/api/v1")

app.include_router(spec_router, prefix="")
app.include_router(styles_stub_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        provider_factory = app.state.provider_factory
        providers_status = await provider_factory.health_check()

        return HealthResponse(
            status="healthy",
            service="mcp-visual-design-service",
            version="0.1.0",
            providers=providers_status,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return degraded but 200 to keep health readable during local/dev tests
        return HealthResponse(
            status="degraded",
            service="mcp-visual-design-service",
            version="0.1.0",
            providers={},
        )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "service": "MCP Visual Design Service",
        "version": "0.1.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )