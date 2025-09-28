"""Pydantic models for Visual Design Request domain (spec entities)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class VisualDesignRequest(BaseModel):
    id: str
    projectId: str
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    references: List[Dict[str, Optional[str]]] = Field(default_factory=list)
    status: str
    createdAt: str
    updatedAt: str


class ConceptBoard(BaseModel):
    id: str
    requestId: str
    iteration: int
    summary: str
    conceptCount: int = 0
    previewImageUrl: Optional[HttpUrl] = None
    status: str


class ConceptItem(BaseModel):
    id: str
    boardId: str
    caption: str
    tags: List[str] = Field(default_factory=list)
    imageUrls: List[HttpUrl] = Field(default_factory=list)
    provenance: Optional[str] = None


class ReviewFeedback(BaseModel):
    id: str
    targetType: str
    targetId: str
    author: str
    text: str
    createdAt: str


class ApprovalRecord(BaseModel):
    id: str
    requestId: str
    iterationApproved: int
    approver: str
    approvedAt: str


