# mcp-visual-design-service

## Service overview and purpose
An MCP server responsible for visual pre-production workflows: storyboards, concept frames, shot moodboards, and style exploration. It orchestrates image generation providers (e.g., FAL, OpenRouter image models), performs prompt templating, and stores resulting assets/metadata for use by the auto-movie platform.

## Technical requirements and dependencies
- Language: Python 3.11+
- Framework: FastAPI for HTTP + MCP protocol adapter for tool calls
- Task queue: Optional Redis/Celery integration for long-running generations
- External providers: FAL text-to-image, image-to-image; OpenRouter image-capable models
- Storage: PayloadCMS Media collection (via REST) or S3-compatible bucket configured by CMS
- Observability: Basic logs; emit structured status events over WebSocket to CMS when available

## API endpoints and interfaces
- HTTP (service-internal / orchestration):
  - POST `/generate/storyboard` { projectId, scenes[], stylePreset, seed } → frames[]
  - POST `/generate/concept` { prompt, refs[], stylePreset } → images[]
  - POST `/upscale` { mediaId, factor } → mediaId
  - GET `/health` → { ok: true }
- MCP tools (for agent flows):
  - `visual.generate_storyboard` (projectId, scenes, style) → asset refs
  - `visual.generate_concepts` (prompt, refs, style) → asset refs
- Events:
  - WebSocket/HTTP callback to CMS: generation-started, progress, completed, failed

## Database schema (if applicable)
No dedicated DB required initially. Persist via PayloadCMS Media collection and attach metadata:
- media.metadata.visual: { type: "storyboard|concept|upscale", source, provider, params, generationId }

## Integration points with PayloadCMS
- Upload generated files to `/api/v1/media/upload` with metadata
- Link results to Projects and Sessions via their IDs
- Optionally register promptTemplates usage in promptsExecuted
- Respect platform constraints: seeded model list; return best possible error messages on failure; no retries/roles for now

## Step-by-step implementation guide
1. Bootstrap FastAPI + MCP server with health endpoint
2. Implement provider clients (FAL/OpenRouter) behind an interface
3. Add request validation (Pydantic) and prompt templating
4. Stream progress events; upload final assets to CMS Media
5. Expose MCP tools for orchestrator and UI usage
6. Add Celery tasks for heavy jobs (optional) and back-pressure via Redis

## Testing strategy
- Unit tests for provider adapters (mock HTTP)
- Contract tests for MCP tools
- Integration test: end-to-end `/generate/storyboard` → media upload
- Error-path tests: provider failure returns structured error

## Deployment considerations
- Containerize with minimal image; mount provider API keys as env vars
- Configure concurrency; GPU node optional
- Network egress to providers; internal access to CMS API and Redis (if used)

