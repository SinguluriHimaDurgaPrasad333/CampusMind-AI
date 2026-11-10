from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CategoryStat(BaseModel):
    category: str
    count: int


class UnansweredQueryItem(BaseModel):
    id: str
    query: str
    max_similarity: float
    reason: str
    created_at: datetime


class AnalyticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_questions_asked: int
    total_chat_sessions: int
    average_latency_ms: float
    satisfaction_rate_percent: float
    total_positive_feedback: int
    total_negative_feedback: int
    unanswered_count: int
    category_distribution: List[CategoryStat]
    recent_unanswered_queries: List[UnansweredQueryItem]
