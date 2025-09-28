# MCP Visual Design Service

AI-powered visual design and asset generation service for movie production. This service handles storyboard generation, concept art creation, and image upscaling through integration with FAL and OpenRouter providers.

## Features

- **Storyboard Generation**: Convert scene descriptions into visual storyboard frames
- **Concept Art Creation**: Generate concept art variations from text descriptions
- **Image Upscaling**: Enhance existing images with AI upscaling
- **Multiple Providers**: Support for FAL and OpenRouter image generation services
- **Style Templates**: Pre-configured visual styles (cinematic, concept-art, photorealistic, etc.)
- **PayloadCMS Integration**: Automatic asset upload and metadata management
- **MCP Protocol**: Tools for LangGraph orchestrator integration
- **REST API**: HTTP endpoints for direct integration

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- FAL API key and/or OpenRouter API key
- PayloadCMS instance running

### Environment Setup

1. Copy environment template:
```bash
cp .env.example .env
```

2. Configure your environment variables:
```bash
# Image Generation Providers
FAL_API_KEY=your-fal-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# PayloadCMS Integration
PAYLOADCMS_API_URL=http://localhost:3000/api
PAYLOADCMS_API_KEY=your-cms-api-key
```

### Development

**Option 1: Docker Compose (Recommended)**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f mcp-visual-design-service

# Health check
curl http://localhost:8004/health
```

**Option 2: Local Development**
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run service
python src/main.py
```

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/              # Unit tests
pytest tests/contract/          # Contract tests
pytest tests/integration/       # Integration tests

# Run with coverage
pytest --cov=src
```

## API Usage

### REST API Endpoints

**Generate Storyboard**
```bash
curl -X POST http://localhost:8004/api/v1/visual/storyboard \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project-123",
    "scenes": [
      {
        "description": "A hero stands on a mountain peak at sunset",
        "mood": "dramatic",
        "camera_angle": "wide shot"
      }
    ],
    "style_preset": "cinematic",
    "aspect_ratio": "16:9"
  }'
```

**Generate Concept Art**
```bash
curl -X POST http://localhost:8004/api/v1/visual/concept \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Futuristic space station floating in nebula",
    "style_preset": "concept-art",
    "variations": 3
  }'
```

**Upscale Image**
```bash
curl -X POST http://localhost:8004/api/v1/visual/upscale \
  -H "Content-Type: application/json" \
  -d '{
    "media_id": "media-123",
    "factor": 2
  }'
```

### MCP Tools (for LangGraph Integration)

The service exposes MCP tools for workflow integration:

- `visual.generate_storyboard()` - Generate storyboard frames
- `visual.generate_concepts()` - Generate concept art
- `visual.upscale_image()` - Upscale existing images
- `visual.health_check()` - Check service health

## Configuration

### Style Presets

Available visual styles:
- `cinematic` - Professional film quality with dramatic lighting
- `concept-art` - Digital painting style for pre-production
- `photorealistic` - High-quality photography style
- `anime` - Anime/manga art style
- `artistic` - Creative and expressive artwork
- `storyboard` - Professional storyboard sketches

### Provider Configuration

**FAL (Primary)**
- Best for: Fast generation, high quality
- Models: flux/schnell, flux/dev, flux-pro
- Features: Text-to-image, image-to-image, upscaling

**OpenRouter (Fallback)**
- Best for: Model variety, cost optimization
- Models: FLUX, Stable Diffusion, Ideogram
- Features: Text-to-image (upscaling limited)

## Architecture

### Core Components

- **FastAPI Application**: REST API and health endpoints
- **Provider Factory**: Manages FAL and OpenRouter integrations
- **Visual Service**: Main business logic for generation workflows
- **Asset Service**: PayloadCMS integration for media management
- **Template Manager**: Style presets and prompt templates
- **MCP Tools**: LangGraph orchestrator integration

### Data Flow

1. **Request** → API endpoint or MCP tool
2. **Validation** → Pydantic models ensure data integrity
3. **Template Application** → Style presets enhance prompts
4. **Provider Selection** → Choose optimal generation service
5. **Generation** → Create images via AI providers
6. **Asset Upload** → Store results in PayloadCMS
7. **Response** → Return asset references and metadata

## Production Deployment

### Docker Production Setup

1. Build production image:
```bash
docker build -t mcp-visual-design-service:latest .
```

2. Run with production configuration:
```bash
docker run -d \
  --name mcp-visual-design-service \
  -p 8004:8004 \
  --env-file .env.production \
  --restart unless-stopped \
  mcp-visual-design-service:latest
```

### Environment Variables (Production)

```bash
# Service
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Security
FAL_API_KEY=secure-fal-key
OPENROUTER_API_KEY=secure-openrouter-key
PAYLOADCMS_API_KEY=secure-cms-key

# Performance
REDIS_URL=redis://production-redis:6379

# Monitoring
WEBSOCKET_ENABLED=true
```

### Health Monitoring

- **Health endpoint**: `GET /health`
- **Metrics**: Provider status, response times, error rates
- **Logging**: Structured JSON logs for production

## Development

### Adding New Providers

1. Implement `BaseProvider` interface
2. Add to `ProviderFactory`
3. Update configuration
4. Add tests

### Adding New Styles

1. Define style template in `TemplateManager`
2. Configure prompts and settings
3. Add to style presets
4. Test with different providers

### Code Quality

```bash
# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/
```

## Troubleshooting

### Common Issues

**Provider API Errors**
- Check API keys are valid and have sufficient credits
- Verify network connectivity to provider APIs
- Check rate limits and quotas

**PayloadCMS Integration**
- Ensure PayloadCMS is running and accessible
- Verify API key has media upload permissions
- Check media collection configuration

**Performance Issues**
- Monitor generation times and adjust timeouts
- Use Redis for background processing
- Implement request queuing for high load

### Logs and Monitoring

```bash
# View logs
docker-compose logs -f mcp-visual-design-service

# Health check
curl http://localhost:8004/health

# Provider status
curl http://localhost:8004/api/v1/visual/providers
```

## License

This service is part of the Movie Generation Platform project.