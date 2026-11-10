from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class CitationItem(BaseModel):
    document_name: str
    category: str
    page_number: int
    score: float
    snippet: str


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Student's natural language question")
    session_id: Optional[str] = Field(None, description="Active chat session UUID, or null to auto-create")


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    message_id: str
    sources: List[CitationItem] = []
    confidence_score: float
    latency_ms: float
    is_grounded: bool
    unanswered: bool = False


class FeedbackRequest(BaseModel):
    message_id: str
    feedback: str = Field(..., pattern="^(like|dislike)$")
    comment: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: List[CitationItem] = []
    confidence_score: float
    latency_ms: float
    feedback: Optional[str] = None
    created_at: datetime


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
