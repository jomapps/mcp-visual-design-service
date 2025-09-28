from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from ..models.spec_entities import (
    VisualDesignRequest as VisualDesignRequestModel,
    ConceptBoard as ConceptBoardModel,
    ConceptItem as ConceptItemModel,
    ApprovalRecord as ApprovalRecordModel,
)
from ..services.spec_store import SpecStore
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory stores
_requests: Dict[str, Dict[str, Any]] = {}
_boards: Dict[str, Dict[str, Any]] = {}
_board_by_request: Dict[str, List[str]] = {}
_concepts_by_board: Dict[str, List[Dict[str, Any]]] = {}


class VisualDesignRequestCreate(BaseModel):
    projectId: str
    title: str
    description: str
    tags: Optional[List[str]] = None
    references: Optional[List[Dict[str, Optional[str]]]] = None


class ConceptBoardCreate(BaseModel):
    summary: str


class ConceptItemsCreate(BaseModel):
    items: List[Dict[str, Any]]


@router.post("/requests")
def create_request(payload: VisualDesignRequestCreate) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat() + "Z"
    rid = str(uuid.uuid4())
    item = SpecStore.create_request(payload.model_dump())
    return VisualDesignRequestModel(**item).model_dump()


@router.get("/requests")
def list_requests(projectId: Optional[str] = None, status: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
    page, next_cursor = SpecStore.list_requests(projectId, status, limit, cursor)
    return {"items": [VisualDesignRequestModel(**i).model_dump() for i in page], "nextCursor": next_cursor}


@router.get("/requests/{rid}")
def get_request(rid: str) -> Dict[str, Any]:
    item = SpecStore.get_request(rid)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return VisualDesignRequestModel(**item).model_dump()


@router.delete("/requests/{rid}")
def delete_request(rid: str):
    SpecStore.delete_request(rid)
    return Response(status_code=204)


@router.post("/requests/{rid}/boards")
def create_board(rid: str, payload: ConceptBoardCreate) -> Dict[str, Any]:
    if not SpecStore.get_request(rid):
        raise HTTPException(status_code=404, detail="Request not found")
    board = SpecStore.create_board(rid, payload.summary)
    return ConceptBoardModel(**board).model_dump()


@router.get("/requests/{rid}/boards")
def list_boards(rid: str) -> List[Dict[str, Any]]:
    if not SpecStore.get_request(rid):
        raise HTTPException(status_code=404, detail="Request not found")
    return [ConceptBoardModel(**b).model_dump() for b in SpecStore.list_boards(rid)]


@router.post("/boards/{board_id}/concepts")
def add_concepts(board_id: str, payload: ConceptItemsCreate) -> List[Dict[str, Any]]:
    if board_id not in SpecStore.state.boards:
        raise HTTPException(status_code=404, detail="Board not found")
    concepts = SpecStore.add_concepts(board_id, payload.items)
    return [ConceptItemModel(**c).model_dump() for c in concepts]


@router.post("/boards/{board_id}/approve")
def approve_board(board_id: str) -> Dict[str, Any]:
    board = SpecStore.state.boards.get(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    rec = SpecStore.approve_board(board_id)
    return ApprovalRecordModel(**rec).model_dump()


@router.get("/requests/{rid}/export")
def export_request(rid: str) -> Dict[str, Any]:
    if not SpecStore.get_request(rid):
        raise HTTPException(status_code=404, detail="Not found")
    return SpecStore.export_request(rid)
