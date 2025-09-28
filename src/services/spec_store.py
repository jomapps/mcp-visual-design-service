"""In-memory store and service for spec endpoints (requests/boards/concepts).

This is a lightweight, test-friendly implementation to satisfy contracts
without requiring external persistence. It can be replaced with a real store.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class _State:
    requests: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    boards: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    board_by_request: Dict[str, List[str]] = field(default_factory=dict)
    concepts_by_board: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


class SpecStore:
    state = _State()

    @staticmethod
    def _now() -> str:
        return datetime.utcnow().isoformat() + "Z"

    @classmethod
    def create_request(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        rid = str(uuid.uuid4())
        item = {
            "id": rid,
            "projectId": data["projectId"],
            "title": data["title"],
            "description": data["description"],
            "tags": data.get("tags") or [],
            "references": data.get("references") or [],
            "status": "Submitted",
            "createdAt": cls._now(),
            "updatedAt": cls._now(),
        }
        cls.state.requests[rid] = item
        cls.state.board_by_request.setdefault(rid, [])
        logger.info("Created request %s for project %s", rid, data["projectId"])
        return item

    @classmethod
    def list_requests(
        cls, project_id: Optional[str], status: Optional[str], limit: int, cursor: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        items = sorted(cls.state.requests.values(), key=lambda i: i.get("createdAt", ""), reverse=True)
        if project_id:
            items = [i for i in items if i.get("projectId") == project_id]
        if status:
            items = [i for i in items if i.get("status") == status]
        try:
            offset = int(cursor) if cursor is not None else 0
        except ValueError:
            offset = 0
        page_limit = max(1, min(limit, 200))
        page = items[offset : offset + page_limit]
        next_cursor = str(offset + page_limit) if offset + page_limit < len(items) else None
        logger.debug("List requests offset=%s limit=%s returned=%s", offset, page_limit, len(page))
        return page, next_cursor

    @classmethod
    def get_request(cls, rid: str) -> Optional[Dict[str, Any]]:
        return cls.state.requests.get(rid)

    @classmethod
    def delete_request(cls, rid: str) -> None:
        if rid in cls.state.requests:
            for bid in cls.state.board_by_request.get(rid, []):
                cls.state.boards.pop(bid, None)
                cls.state.concepts_by_board.pop(bid, None)
            cls.state.board_by_request.pop(rid, None)
            cls.state.requests.pop(rid, None)
            logger.info("Deleted request %s with cascade", rid)

    @classmethod
    def create_board(cls, rid: str, summary: str) -> Dict[str, Any]:
        iteration = len(cls.state.board_by_request.get(rid, [])) + 1
        bid = str(uuid.uuid4())
        board = {
            "id": bid,
            "requestId": rid,
            "iteration": iteration,
            "summary": summary,
            "conceptCount": 0,
            "status": "Initial" if iteration == 1 else "Revised",
        }
        cls.state.boards[bid] = board
        cls.state.board_by_request.setdefault(rid, []).append(bid)
        cls.state.concepts_by_board.setdefault(bid, [])
        logger.info("Created board %s for request %s (iteration %s)", bid, rid, iteration)
        return board

    @classmethod
    def list_boards(cls, rid: str) -> List[Dict[str, Any]]:
        return [cls.state.boards[bid] for bid in cls.state.board_by_request.get(rid, []) if bid in cls.state.boards]

    @classmethod
    def add_concepts(cls, board_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        concepts = cls.state.concepts_by_board.setdefault(board_id, [])
        for item in items:
            concepts.append(
                {
                    "id": str(uuid.uuid4()),
                    "boardId": board_id,
                    "caption": item.get("caption", ""),
                    "tags": item.get("tags", []),
                    "imageUrls": item.get("imageUrls", []),
                    "provenance": item.get("provenance"),
                }
            )
        if board_id in cls.state.boards:
            cls.state.boards[board_id]["conceptCount"] = len(concepts)
        logger.info("Added %s concept(s) to board %s", len(items), board_id)
        return concepts

    @classmethod
    def approve_board(cls, board_id: str) -> Dict[str, Any]:
        board = cls.state.boards.get(board_id)
        assert board is not None
        board["status"] = "Approved"
        rec = {
            "id": str(uuid.uuid4()),
            "requestId": board["requestId"],
            "iterationApproved": board["iteration"],
            "approver": "system",
            "approvedAt": cls._now(),
        }
        logger.info("Approved board %s for request %s", board_id, board["requestId"])
        return rec

    @classmethod
    def export_request(cls, rid: str) -> Dict[str, Any]:
        boards = [cls.state.boards[bid] for bid in cls.state.board_by_request.get(rid, []) if bid in cls.state.boards]
        concepts: List[Dict[str, Any]] = []
        for bid in cls.state.board_by_request.get(rid, []):
            concepts.extend(cls.state.concepts_by_board.get(bid, []))
        return {
            "request": cls.state.requests[rid],
            "boards": boards,
            "concepts": concepts,
        }


