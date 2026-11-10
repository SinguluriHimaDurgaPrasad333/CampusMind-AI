from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.evaluator import evaluation_service
from app.schemas.evaluation import EvaluationBenchmarkResponse

router = APIRouter(tags=["Evaluation"])


@router.post("/evaluate", response_model=EvaluationBenchmarkResponse)
def run_evaluation_benchmark(db: Session = Depends(get_db)):
    """
    Executes the full RAG benchmark over the labelled question evaluation dataset.
    Computes Recall@1, Recall@3, Recall@K, Precision@K, MRR, Groundedness, and Latency.
    """
    return evaluation_service.run_benchmark(db)
