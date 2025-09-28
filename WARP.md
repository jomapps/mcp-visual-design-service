# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

The MCP Visual Design Service is a Python-based FastAPI service that handles visual pre-production workflows for AI movie generation. It orchestrates image generation providers (FAL, OpenRouter), manages prompt templating, and integrates with PayloadCMS for asset storage. The service implements both REST HTTP endpoints and MCP (Model Context Protocol) tools for seamless integration with the orchestration layer.

## Key Commands

### Development Server
```bash
# Start development server with auto-reload
python -m uvicorn src.main:app --host 0.0.0.0 --port 8004 --reload

# Alternative: Run directly
python src/main.py

# Health check
curl http://localhost:8004/health
```

### Dependencies
```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies  
pip install -r requirements-dev.txt

# Using Poetry (alternative)
poetry install
```

### Testing
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/              # Provider adapters and validation
pytest tests/contract/          # MCP tools contract tests
pytest tests/integration/       # End-to-end workflows
pytest tests/performance/       # Generation time and throughput

# Run single test with verbose output
pytest tests/integration/test_storyboard_generation.py -v

# Test with provider mocks
pytest tests/unit/test_provider_adapters.py -v
```

### Code Quality
```bash
# Lint code
ruff check src/ tests/

# Format code
ruff format src/ tests/

# Type checking (if using mypy)
mypy src/
```

### Environment Setup
```bash
# Copy example environment file
cp .env.example .env

# Required environment variables for development
export FAL_API_KEY=your-fal-api-key
export OPENROUTER_API_KEY=your-openrouter-key
export PAYLOADCMS_API_URL=http://localhost:3000/api
export PAYLOADCMS_API_KEY=your-cms-key
```

## Architecture

### Core Components

- **FastAPI Application** (`src/main.py`): HTTP REST server with MCP tool registration
- **Provider Orchestrator** (`src/services/visual_service.py`): Main business logic for visual generation workflows
- **Provider Adapters** (`src/providers/`): FAL and OpenRouter API integrations behind common interface
- **Asset Management** (`src/lib/assets.py`): PayloadCMS integration for media upload and storage
- **MCP Tools** (`src/tools/`): Tool implementations for LangGraph orchestrator integration
- **Prompt Templates** (`src/templates/`): Configurable prompt templates for different visual styles

### Visual Generation Flow

#### Storyboard Generation
1. **Input Validation**: Validate project ID, scenes array, and style preset
2. **Prompt Assembly**: Apply template transformations to scene descriptions
3. **Provider Selection**: Choose optimal provider based on style requirements and availability
4. **Batch Processing**: Generate frames in parallel with progress tracking
5. **Asset Upload**: Store generated images in PayloadCMS with metadata
6. **Response Assembly**: Return asset references with generation metadata

#### Concept Art Generation
1. **Reference Processing**: Analyze provided reference images if any
2. **Style Application**: Apply style preset to prompt template
3. **Generation**: Create concept variations using selected provider
4. **Quality Check**: Validate generated assets meet requirements
5. **Storage**: Upload to CMS with project linkage

### Provider Integration Strategy

**FAL Integration** (`src/providers/fal_provider.py`):
- Primary for photorealistic and cinematic styles
- Handles text-to-image and image-to-image workflows
- Optimized for speed and quality balance

**OpenRouter Integration** (`src/providers/openrouter_provider.py`):
- Fallback for when FAL is unavailable
- Access to multiple image generation models
- Cost optimization through model selection

**Provider Interface** (`src/providers/base.py`):
```python
class BaseProvider:
    async def generate_image(self, prompt: str, params: Dict) -> ImageResult
    async def upscale_image(self, image_url: str, factor: int) -> ImageResult  
    async def check_health(self) -> ProviderHealth
```

### MCP Tools Integration

The service exposes MCP tools for the LangGraph orchestrator:

**Available Tools:**
- `visual.generate_storyboard(project_id, scenes, style)` → asset references
- `visual.generate_concepts(prompt, refs, style)` → asset references  
- `visual.upscale_image(media_id, factor)` → enhanced asset reference

**Tool Implementation Pattern:**
```python
@mcp_tool
async def generate_storyboard(project_id: str, scenes: List[Scene], style: str):
    # Validate inputs
    # Process through visual service
    # Return structured response
```

### PayloadCMS Integration Strategy

- **Media Upload**: POST `/api/v1/media/upload` with generated images
- **Metadata Storage**: Attach visual-specific metadata to media records
- **Project Linkage**: Associate assets with project and session IDs
- **Asset Retrieval**: Enable frontend access to generated visuals

### Error Handling & Resilience

- **Provider Failover**: Automatic fallback between FAL and OpenRouter
- **Rate Limiting**: Built-in backoff for provider API limits
- **Partial Success**: Return successful generations even if some fail
- **Progress Tracking**: WebSocket events for long-running generations
- **Structured Errors**: Consistent error format across HTTP and MCP interfaces

## Development Patterns

### Adding New Visual Generation Types
1. Define request/response models in `src/models/visual.py`
2. Add business logic method in `src/services/visual_service.py`
3. Implement HTTP endpoint in `src/main.py`
4. Create corresponding MCP tool in `src/tools/visual_tools.py`
5. Add contract tests in `tests/contract/`
6. Add integration test with provider mocks

### Provider Integration Pattern
1. Implement `BaseProvider` interface in `src/providers/`
2. Add provider-specific configuration in environment
3. Register provider in `src/services/provider_factory.py`
4. Add unit tests with HTTP mocks
5. Add health check endpoint integration

### Template System Usage
```python
# Apply template to scene description
template = TemplateManager.get_template("cinematic-storyboard")
enhanced_prompt = template.apply({
    "scene": scene.description,
    "style": style_preset,
    "mood": scene.mood
})
```

### Asset Metadata Pattern
```python
metadata = {
    "visual": {
        "type": "storyboard|concept|upscale",
        "source": "fal|openrouter", 
        "provider": provider_name,
        "params": generation_params,
        "generation_id": unique_id
    }
}
```

## Environment Configuration

### Required Environment Variables
```bash
# Image Generation Providers
FAL_API_KEY=your-fal-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# PayloadCMS Integration  
PAYLOADCMS_API_URL=http://localhost:3000/api
PAYLOADCMS_API_KEY=your-cms-api-key

# Service Configuration
MCP_VISUAL_SERVICE_PORT=8004
MCP_VISUAL_SERVICE_HOST=0.0.0.0

# Optional: Redis for Celery background tasks
REDIS_URL=redis://localhost:6379

# Optional: WebSocket events
WEBSOCKET_ENABLED=true
PAYLOADCMS_WEBSOCKET_URL=ws://localhost:3000/ws
```

### Development vs Production
- **Development**: Mock providers available for testing without API keys
- **Production**: Real provider integration with proper error handling
- **Testing**: Provider mocks ensure consistent test results

## Performance Characteristics

- **Storyboard Generation**: 30-60 seconds for 6-12 frames (provider dependent)
- **Concept Art**: 5-15 seconds per image
- **Upscaling**: 10-30 seconds depending on factor and source image
- **Concurrent Generations**: Limited by provider rate limits (typically 5-10 parallel)
- **Asset Upload**: 1-3 seconds per image to PayloadCMS

## Integration with Platform

### Brain Service Communication
The service does NOT directly connect to the MCP Brain Service. All AI/ML operations go through the orchestration layer which handles brain service communication.

### Platform Service Dependencies
- **PayloadCMS**: Required for asset storage and metadata
- **LangGraph Orchestrator**: Consumes MCP tools for workflow integration
- **Redis** (Optional): For background task processing via Celery

### Startup Order Dependencies
1. PayloadCMS must be running (port 3000)
2. Redis (optional, if using Celery)
3. Start MCP Visual Design Service (port 8004)
4. Service registers with orchestrator automatically

## Testing Strategy

### Test Categories
- **Unit Tests**: Provider adapters, template system, validation logic
- **Contract Tests**: MCP tool interfaces and HTTP API contracts  
- **Integration Tests**: End-to-end generation workflows with mocked providers
- **Performance Tests**: Generation time benchmarks and throughput testing

### Mock Strategy
- **Provider Mocks**: Simulate FAL/OpenRouter responses for consistent testing
- **CMS Mocks**: Mock PayloadCMS upload endpoints
- **Asset Fixtures**: Pre-generated test images for validation

### Running Tests During Development
```bash
# Start service with test configuration
ENVIRONMENT=test python src/main.py

# Run contract tests
pytest tests/contract/ -v

# Run integration tests with provider mocks
pytest tests/integration/ -v --mock-providers

# Performance benchmarks
pytest tests/performance/ -v -s
```