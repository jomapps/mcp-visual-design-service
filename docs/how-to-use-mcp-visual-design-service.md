# How to Use MCP Visual Design Service

This comprehensive guide explains how to use the MCP Visual Design Service for AI-powered visual content generation in movie production workflows.

## Table of Contents

1. [Service Overview](#service-overview)
2. [Quick Start](#quick-start)
3. [Storyboard Generation](#storyboard-generation)
4. [Concept Art Creation](#concept-art-creation)
5. [Image Upscaling](#image-upscaling)
6. [Style Templates](#style-templates)
7. [Provider Selection](#provider-selection)
8. [MCP Tools Usage](#mcp-tools-usage)
9. [REST API Usage](#rest-api-usage)
10. [Performance & Timing](#performance--timing)
11. [Error Handling](#error-handling)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

## Service Overview

The MCP Visual Design Service transforms text descriptions into high-quality visual assets for movie pre-production:

- **Storyboard Generation**: Scene descriptions → Visual storyboard frames
- **Concept Art Creation**: Ideas → Professional concept artwork
- **Image Upscaling**: Low-res images → High-resolution enhanced versions
- **Style Consistency**: Unified visual language across your project
- **Multi-Provider**: FAL and OpenRouter integration with automatic fallback

**Service Endpoint**: `http://localhost:8004`  
**Health Check**: `GET /health`  
**Documentation**: `GET /docs` (FastAPI auto-docs)

## Quick Start

### Prerequisites

1. **Service Running**: Ensure the visual design service is started
2. **API Keys**: Configure at least one provider (FAL or OpenRouter)
3. **PayloadCMS**: Required for asset storage and retrieval
4. **Project Setup**: Have a project ID for asset organization

### Basic Health Check

```bash
# Check service status
curl http://localhost:8004/health

# Expected response
{
  "status": "healthy",
  "service": "mcp-visual-design-service", 
  "version": "0.1.0",
  "providers": {
    "fal": "healthy",
    "openrouter": "healthy"
  }
}
```

### Available Capabilities

```bash
# Get provider information
curl http://localhost:8004/api/v1/visual/providers

# Get available styles
curl http://localhost:8004/api/v1/visual/styles
```

## Storyboard Generation

Convert scene descriptions into visual storyboard frames for pre-production planning.

### Basic Storyboard Request

```bash
curl -X POST http://localhost:8004/api/v1/visual/storyboard \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "movie-project-123",
    "scenes": [
      {
        "description": "A lone astronaut stands on the edge of a massive crater on an alien planet, looking up at two moons in the purple sky",
        "mood": "contemplative",
        "camera_angle": "wide shot",
        "lighting": "dramatic moonlight"
      },
      {
        "description": "Close-up of the astronaut's helmet reflection showing the alien landscape",
        "mood": "mysterious", 
        "camera_angle": "extreme close-up",
        "lighting": "rim lighting"
      }
    ],
    "style_preset": "cinematic",
    "aspect_ratio": "16:9",
    "quality": "standard"
  }'
```

### Storyboard Response Format

```json
{
  "generation_id": "gen-uuid-12345",
  "project_id": "movie-project-123",
  "status": "completed",
  "progress": 1.0,
  "total_scenes": 2,
  "completed_scenes": 2,
  "assets": [
    {
      "id": "asset-id-1",
      "url": "https://cms.local/media/storyboard_gen-uuid-12345_scene_001.png",
      "type": "storyboard",
      "width": 1024,
      "height": 576,
      "provider": "fal",
      "model": "fal-ai/flux/schnell",
      "prompt": "A cinematic lone astronaut stands on the edge of a massive crater on an alien planet, looking up at two moons in the purple sky, contemplative mood, wide shot, dramatic moonlight, 35mm film, cinematic composition..."
    }
  ],
  "error_message": null
}
```

### Scene Description Best Practices

**Effective Scene Descriptions:**
- Be specific about visual elements: "red sports car" vs "car"
- Include spatial relationships: "in the foreground", "behind the building"
- Specify lighting conditions: "golden hour", "harsh shadows", "soft window light"
- Mention important props and set pieces
- Keep descriptions focused (1-2 sentences max)

**Good Examples:**
```json
{
  "description": "Medieval knight in gleaming armor kneels before a stone altar in a candlelit cathedral, shafts of colored light streaming through stained glass windows",
  "mood": "reverent",
  "camera_angle": "low angle",
  "lighting": "dramatic cathedral lighting"
}
```

**Avoid:**
```json
{
  "description": "A person does something in a place",
  "mood": "good",
  "camera_angle": "normal"
}
```

### Expected Generation Time

- **1-3 scenes**: 30-60 seconds
- **4-6 scenes**: 1-2 minutes  
- **7-12 scenes**: 2-4 minutes
- **Factors**: Provider speed, image complexity, current load

## Concept Art Creation

Generate concept art variations for characters, environments, props, and visual development.

### Basic Concept Request

```bash
curl -X POST http://localhost:8004/api/v1/visual/concept \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Futuristic cyberpunk cityscape with neon-lit skyscrapers, flying cars, and holographic advertisements reflecting on wet streets",
    "project_id": "movie-project-123",
    "style_preset": "concept-art",
    "variations": 3,
    "aspect_ratio": "16:9",
    "quality": "high"
  }'
```

### Concept Art Response

```json
{
  "generation_id": "concept-uuid-67890",
  "project_id": "movie-project-123", 
  "status": "completed",
  "progress": 1.0,
  "assets": [
    {
      "id": "concept-asset-1",
      "url": "https://cms.local/media/concept_gen-uuid_var_01.png",
      "type": "concept",
      "width": 1024,
      "height": 576,
      "provider": "fal",
      "prompt": "Concept art of Futuristic cyberpunk cityscape with neon-lit skyscrapers, flying cars, and holographic advertisements reflecting on wet streets, digital painting, detailed illustration..."
    }
  ]
}
```

### Concept Art Use Cases

**Character Design:**
```json
{
  "prompt": "Steampunk inventor with brass goggles, leather apron, and mechanical arm, standing in a workshop filled with clockwork contraptions",
  "style_preset": "concept-art",
  "variations": 4
}
```

**Environment Design:**
```json
{
  "prompt": "Ancient library with towering bookshelves, floating books, magical orbs of light, and a spiral staircase disappearing into shadows above",
  "style_preset": "concept-art", 
  "aspect_ratio": "1:1"
}
```

**Vehicle/Prop Design:**
```json
{
  "prompt": "Sleek space fighter with angular wings, glowing blue engines, and weathered hull plating, shown from multiple angles",
  "style_preset": "photorealistic",
  "variations": 2
}
```

### Using Reference Images

```json
{
  "prompt": "Medieval castle redesigned with modern materials and lighting",
  "reference_images": [
    "https://example.com/reference-castle.jpg",
    "https://example.com/modern-architecture.jpg"
  ],
  "style_preset": "concept-art"
}
```

## Image Upscaling

Enhance existing images with AI upscaling for higher resolution and improved quality.

### Basic Upscale Request

```bash
curl -X POST http://localhost:8004/api/v1/visual/upscale \
  -H "Content-Type: application/json" \
  -d '{
    "media_id": "existing-asset-id-123",
    "factor": 2,
    "project_id": "movie-project-123",
    "quality": "high"
  }'
```

### Upscale Response

```json
{
  "generation_id": "upscale-uuid-54321",
  "project_id": "movie-project-123",
  "status": "completed", 
  "progress": 1.0,
  "original_asset_id": "existing-asset-id-123",
  "upscaled_asset": {
    "id": "upscaled-asset-id",
    "url": "https://cms.local/media/upscaled_gen-uuid_2x.png",
    "type": "upscale",
    "width": 2048,
    "height": 2048,
    "provider": "fal"
  }
}
```

### Upscaling Options

**Upscale Factors:**
- `2`: Double resolution (1024x1024 → 2048x2048)
- `4`: Quadruple resolution (512x512 → 2048x2048)

**Quality Settings:**
- `standard`: Balanced speed and quality
- `high`: Maximum quality (slower)

**Expected Times:**
- **2x upscale**: 10-20 seconds
- **4x upscale**: 20-45 seconds

## Style Templates

The service includes 6 pre-configured style templates optimized for different visual needs.

### Available Styles

#### 1. Cinematic
**Best for**: Storyboards, film-quality scenes  
**Characteristics**: 35mm film look, dramatic lighting, professional cinematography  
**Settings**: 30 steps, 16:9 aspect ratio

```json
{
  "style_preset": "cinematic",
  "description": "Hero walks through fog-covered battlefield at dawn"
}
```

#### 2. Concept Art  
**Best for**: Pre-production artwork, design exploration  
**Characteristics**: Digital painting style, detailed illustration, matte painting quality  
**Settings**: 25 steps, 16:9 aspect ratio

```json
{
  "style_preset": "concept-art", 
  "description": "Ancient temple hidden in jungle canopy with vines and mysterious light"
}
```

#### 3. Photorealistic
**Best for**: Reference imagery, realistic visualization  
**Characteristics**: Photography-like quality, realistic lighting, sharp detail  
**Settings**: 35 steps, 3:2 aspect ratio

```json
{
  "style_preset": "photorealistic",
  "description": "Modern apartment interior with floor-to-ceiling windows and city view"
}
```

#### 4. Anime
**Best for**: Animation pre-production, stylized content  
**Characteristics**: High-quality anime art, cel shading, vibrant colors  
**Settings**: 25 steps, 16:9 aspect ratio

```json
{
  "style_preset": "anime",
  "description": "Young warrior with glowing sword stands on mountain peak under starry sky"
}
```

#### 5. Artistic
**Best for**: Creative exploration, unique visual treatments  
**Characteristics**: Expressive artwork, creative composition, artistic vision  
**Settings**: 28 steps, 1:1 aspect ratio

```json
{
  "style_preset": "artistic",
  "description": "Abstract representation of time flowing through a clockwork mechanism"
}
```

#### 6. Storyboard
**Best for**: Quick storyboard sketches, pre-visualization  
**Characteristics**: Professional storyboard art, clear composition, sketch-like quality  
**Settings**: 20 steps, 16:9 aspect ratio

```json
{
  "style_preset": "storyboard",
  "description": "Character runs down corridor while explosions bloom behind them"
}
```

### Style Comparison Examples

**Same prompt, different styles:**

*Prompt: "Dragon perched on castle tower under stormy sky"*

- **Cinematic**: Film-quality with dramatic storm lighting and atmospheric effects
- **Concept Art**: Detailed digital painting with rich textures and artistic composition  
- **Photorealistic**: Realistic dragon and architecture with natural storm lighting
- **Anime**: Stylized dragon with clean lines and vibrant storm effects
- **Artistic**: Creative interpretation with expressive brushstrokes and color
- **Storyboard**: Clean sketch showing clear action and composition

## Provider Selection

The service supports multiple image generation providers with automatic fallback.

### Provider Characteristics

#### FAL (Primary Provider)
**Strengths:**
- Fast generation (5-15 seconds typical)
- High quality results
- Reliable upscaling
- Good for cinematic and photorealistic styles

**Models:**
- `fal-ai/flux/schnell` (fast, standard quality)
- `fal-ai/flux/dev` (slower, higher quality)
- `fal-ai/flux-pro` (premium quality)

#### OpenRouter (Fallback Provider)  
**Strengths:**
- Model variety
- Cost optimization
- Good for artistic and anime styles

**Models:**
- `black-forest-labs/flux-1.1-pro`
- `stability-ai/stable-diffusion-3.5-large`
- `ideogram-ai/ideogram-v2`

### Manual Provider Selection

```json
{
  "prompt": "Your scene description",
  "provider_preference": "fal",
  "style_preset": "cinematic"
}
```

### Provider Status Monitoring

```bash
# Check provider health and capabilities
curl http://localhost:8004/api/v1/visual/providers

# Response shows:
{
  "providers": ["fal", "openrouter"],
  "models": {
    "fal": ["fal-ai/flux/schnell", "fal-ai/flux/dev"],
    "openrouter": ["black-forest-labs/flux-1.1-pro"]
  },
  "styles": ["photorealistic", "cinematic", "concept-art"],
  "health": {
    "fal": "healthy",
    "openrouter": "degraded"
  }
}
```

## MCP Tools Usage

The service provides MCP tools for integration with LangGraph orchestrator workflows.

### Tool: visual.generate_storyboard

```python
# In LangGraph workflow
result = await mcp_client.call_tool(
    "visual.generate_storyboard",
    {
        "project_id": "project-123",
        "scenes": [
            {
                "description": "Hero enters dark forest clearing",
                "mood": "ominous",
                "camera_angle": "wide shot"
            }
        ],
        "style_preset": "cinematic",
        "aspect_ratio": "16:9"
    }
)

# Returns
{
    "success": True,
    "generation_id": "gen-12345",
    "assets": [{"id": "asset-1", "url": "...", "type": "storyboard"}],
    "completed_scenes": 1,
    "total_scenes": 1
}
```

### Tool: visual.generate_concepts

```python
result = await mcp_client.call_tool(
    "visual.generate_concepts", 
    {
        "prompt": "Futuristic space station command center",
        "project_id": "project-123",
        "style_preset": "concept-art",
        "variations": 2
    }
)
```

### Tool: visual.upscale_image

```python
result = await mcp_client.call_tool(
    "visual.upscale_image",
    {
        "media_id": "existing-asset-123",
        "factor": 2,
        "project_id": "project-123"
    }
)
```

### Tool: visual.health_check

```python
status = await mcp_client.call_tool("visual.health_check", {})

# Returns service and provider health information
{
    "success": True,
    "service": "mcp-visual-design-service",
    "providers": {"fal": "healthy"},
    "capabilities": {
        "supported_models": ["fal-ai/flux/schnell"],
        "operations": ["storyboard", "concept", "upscale"]
    }
}
```

## REST API Usage

Complete REST API reference for direct HTTP integration.

### Authentication
Currently no authentication required for development. In production, API keys may be required.

### Content Types
- Request: `application/json`
- Response: `application/json`

### Error Responses
```json
{
  "detail": "Error description",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### Rate Limiting
- No explicit rate limits
- Limited by provider API limits
- Concurrent requests handled automatically

### Async Operations
All generation operations are asynchronous but return results immediately. For longer operations, consider polling the health endpoint or implementing webhooks.

## Performance & Timing

### Expected Generation Times

| Operation | Scenes/Images | Standard Quality | High Quality |
|-----------|---------------|------------------|--------------|
| Storyboard | 1-3 scenes | 30-60 seconds | 45-90 seconds |
| Storyboard | 4-6 scenes | 1-2 minutes | 1.5-3 minutes |
| Storyboard | 7-12 scenes | 2-4 minutes | 3-6 minutes |
| Concept Art | 1 variation | 5-15 seconds | 10-25 seconds |
| Concept Art | 3 variations | 15-45 seconds | 30-75 seconds |
| Upscale 2x | Single image | 10-20 seconds | 15-30 seconds |
| Upscale 4x | Single image | 20-45 seconds | 30-60 seconds |

### Performance Factors

**Faster Generation:**
- Use `standard` quality setting
- Prefer FAL provider when available
- Use `fal-ai/flux/schnell` model
- Simpler prompts and compositions

**Slower but Higher Quality:**
- Use `high` quality setting  
- Complex scene descriptions
- Multiple variations or upscaling factors
- Peak usage times

### Optimization Tips

1. **Batch Operations**: Process multiple scenes in single storyboard request
2. **Quality Settings**: Use `standard` for drafts, `high` for finals
3. **Provider Selection**: Check provider health before large batches
4. **Aspect Ratios**: Use recommended ratios for each style template
5. **Concurrent Limits**: Service automatically manages concurrency

## Error Handling

### Common Error Types

#### Provider Errors
```json
{
  "status": "failed",
  "error_message": "FAL API error: Insufficient credits"
}
```

**Solutions:**
- Check API key validity and credits
- Verify provider service status
- Try alternate provider

#### Validation Errors
```json
{
  "detail": "Invalid request: scenes list cannot be empty",
  "status_code": 400
}
```

**Solutions:**
- Validate request format
- Check required fields
- Review parameter limits

#### Resource Errors
```json
{
  "status": "failed", 
  "error_message": "Media media-123 not found"
}
```

**Solutions:**
- Verify media ID exists in PayloadCMS
- Check project permissions
- Ensure asset accessibility

### Error Recovery Strategies

**Automatic Fallback:**
- Service automatically tries OpenRouter if FAL fails
- Graceful degradation with reduced quality if needed

**Retry Logic:**
- Implement exponential backoff for temporary failures
- Check provider health before retrying
- Maximum 3 retry attempts recommended

**Partial Success Handling:**
```json
{
  "status": "completed",
  "completed_scenes": 2,
  "total_scenes": 3,
  "assets": [...], 
  "error_message": "Scene 3 generation failed: timeout"
}
```

## Best Practices

### Project Organization

**Use Consistent Project IDs:**
```json
{
  "project_id": "movie-title-2025-preproduction"
}
```

**Organize by Sequence:**
```json
{
  "project_id": "movie-title-2025",
  "scenes": [
    {"description": "Seq001_Shot010: Character enters tavern"},
    {"description": "Seq001_Shot020: Close-up of character's reaction"}
  ]
}
```

### Prompt Engineering

**Be Specific:**
- Good: "Victorian detective in dark coat examines bloody knife on oak desk by candlelight"
- Poor: "Person looks at thing on table"

**Include Visual Context:**
- Camera angles: "low angle", "bird's eye view", "over-the-shoulder"
- Lighting: "golden hour", "harsh shadows", "soft diffused light"
- Mood: "tense", "romantic", "mysterious", "triumphant"

**Layer Details:**
1. Main subject and action
2. Environment and setting  
3. Lighting and atmosphere
4. Camera perspective
5. Style notes

### Workflow Integration

**Storyboard Workflow:**
1. Generate rough storyboard with `standard` quality
2. Review and select best frames
3. Regenerate key frames with `high` quality
4. Upscale final selections for presentation

**Concept Development:**
1. Start with broad concepts using `artistic` style
2. Refine promising directions with `concept-art` style
3. Create variations of approved concepts
4. Generate photorealistic references for final production

### Asset Management

**Naming Conventions:**
- Include project, sequence, and shot information
- Use timestamps for version control
- Tag assets with purpose (storyboard, concept, reference)

**Quality Control:**
- Review generated assets before approval
- Keep original prompts and settings for regeneration
- Document successful prompt patterns

## Troubleshooting

### Service Won't Start

**Check Dependencies:**
```bash
# Verify Python version
python --version  # Should be 3.11+

# Check required packages
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# Test configuration
python -c "from src.config import settings; print(settings)"
```

**Environment Issues:**
```bash
# Verify environment file
cat .env

# Check required variables
echo $FAL_API_KEY
echo $PAYLOADCMS_API_URL
```

### Generation Failures

**Provider API Issues:**
```bash
# Test provider directly
curl -H "Authorization: Key $FAL_API_KEY" https://fal.run/fal-ai/flux/schnell
```

**PayloadCMS Connection:**
```bash
# Test CMS connectivity  
curl -H "Authorization: API-Key $PAYLOADCMS_API_KEY" $PAYLOADCMS_API_URL/media?limit=1
```

### Performance Issues

**Slow Generation Times:**
- Check provider health: `GET /api/v1/visual/providers`
- Monitor system resources (CPU, memory, network)
- Reduce concurrent requests
- Use `standard` quality for testing

**Memory Issues:**
- Restart service if memory usage high
- Reduce batch sizes for large storyboards
- Clear temporary files periodically

### Quality Issues

**Poor Image Quality:**
- Use `high` quality setting
- Try different style presets
- Improve prompt specificity
- Check if provider supports requested features

**Inconsistent Styles:**
- Use same style preset across related scenes
- Include character/environment descriptions consistently
- Consider using reference images for consistency

### Integration Issues

**MCP Tools Not Working:**
- Verify MCP protocol version compatibility
- Check LangGraph orchestrator connection
- Test tools individually before workflow integration

**PayloadCMS Upload Failures:**
- Verify media collection permissions
- Check file size limits
- Ensure API key has upload privileges

### Getting Help

**Debug Information:**
```bash
# Service logs
docker-compose logs -f mcp-visual-design-service

# Health check with details
curl http://localhost:8004/health

# Provider capabilities
curl http://localhost:8004/api/v1/visual/providers
```

**Support Resources:**
- Check service documentation: `/docs`
- Review error logs for specific issues
- Test with minimal examples first
- Verify all dependencies are properly configured

---

This service is designed to provide reliable, high-quality visual generation for movie pre-production. With proper setup and following these guidelines, you should achieve consistent, professional results for your creative projects.