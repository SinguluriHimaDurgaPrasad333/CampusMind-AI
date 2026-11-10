from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class EvaluationResultItem(BaseModel):
    question_id: str
    question: str
    expected_answer: str
    generated_answer: str
    expected_document: str
    retrieved_documents: List[str]
    retrieval_hit: bool
    retrieval_rank: Optional[int] = None
    similarity_score: float
    groundedness_score: float
    latency_ms: float


class EvaluationBenchmarkResponse(BaseModel):
    total_samples: int
    recall_at_1: float
    recall_at_3: float
    recall_at_k: float  # recall @ top_k
    precision_at_k: float
    mean_reciprocal_rank: float
    average_groundedness: float
    average_latency_ms: float
    unanswered_rate_percent: float
    evaluated_at: datetime
    detailed_results: List[EvaluationResultItem] = []
