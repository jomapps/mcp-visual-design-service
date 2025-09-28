# MCP Visual Design Service — Implementation Overview

## Summary
Standalone FastAPI service for visual design workflows (requests → boards → concepts → approval → export). Contracts aligned with feature spec `specs/001-i-have-my/` and OpenAPI (`specs/001-i-have-my/contracts/openapi.yaml`).

## Endpoints (Spec Layer)
- POST `/requests`
- GET `/requests`
- GET `/requests/{id}`
- DELETE `/requests/{id}`
- POST `/requests/{id}/boards`
- GET `/requests/{id}/boards`
- POST `/boards/{boardId}/concepts`
- POST `/boards/{boardId}/approve`
- GET `/requests/{id}/export`

## App Structure
- `src/main.py` — app, health, router mounting
- `src/routers/spec_requests.py` — spec endpoints (in-memory)
- `src/services/spec_store.py` — in-memory store (test-friendly)
- `src/models/spec_entities.py` — pydantic models for spec entities
- `src/routers/styles_stub.py` — styles info stub for tests

## Testing
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

## Notes
- ENV: `ENVIRONMENT=test` skips heavy provider checks; health degrades gracefully.
- Pagination target: <500ms for 200 items (validated in unit test).
- Future: replace `SpecStore` with real persistence and wire MCP calls to brain service.

