import json
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import EvaluationRun
from app.rag.retriever import retriever
from app.rag.llm import llm_service, UNAVAILABLE_INFO_MESSAGE
from app.schemas.evaluation import EvaluationBenchmarkResponse, EvaluationResultItem


class EvaluationService:
    def __init__(self, dataset_path: str = None):
        self.dataset_path = dataset_path or settings.EVALUATION_DATASET_PATH

    def load_dataset(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.dataset_path):
            return []
        try:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[EvaluationService] Failed to load evaluation dataset: {e}")
            return []

    def compute_groundedness(self, generated: str, reference: str) -> float:
        """Calculate lexical overlap between reference answer and generated text."""
        if not generated or generated == UNAVAILABLE_INFO_MESSAGE:
            return 0.0
        ref_tokens = set(reference.lower().split()) - {"the", "is", "a", "an", "of", "and", "in", "to", "for"}
        gen_tokens = set(generated.lower().split())
        if not ref_tokens:
            return 1.0
        overlap = len(ref_tokens.intersection(gen_tokens))
        return min(1.0, round(overlap / len(ref_tokens), 4))

    def run_benchmark(self, db: Session = None) -> EvaluationBenchmarkResponse:
        dataset = self.load_dataset()
        if not dataset:
            return EvaluationBenchmarkResponse(
                total_samples=0,
                recall_at_1=0.0,
                recall_at_3=0.0,
                recall_at_k=0.0,
                precision_at_k=0.0,
                mean_reciprocal_rank=0.0,
                average_groundedness=0.0,
                average_latency_ms=0.0,
                unanswered_rate_percent=0.0,
                evaluated_at=datetime.now(timezone.utc),
                detailed_results=[]
            )

        total_samples = len(dataset)
        hits_at_1 = 0
        hits_at_3 = 0
        hits_at_k = 0
        sum_precision = 0.0
        sum_mrr = 0.0
        sum_groundedness = 0.0
        sum_latency = 0.0
        unanswered_count = 0

        detailed_results: List[EvaluationResultItem] = []

        for sample in dataset:
            q_id = sample.get("question_id", "Q")
            query = sample.get("question", "")
            expected_answer = sample.get("expected_answer", "")
            target_doc = sample.get("reference_document", "")

            start_t = time.perf_counter()
            retrieval_res = retriever.retrieve(query)
            answer, is_grounded = llm_service.generate_answer(
                query, retrieval_res.chunks, retrieval_res.citations, retrieval_res.is_confident
            )
            elapsed_ms = (time.perf_counter() - start_t) * 1000
            sum_latency += elapsed_ms

            retrieved_doc_names = [c.document_name for c in retrieval_res.chunks]

            # Check target document presence and rank
            target_rank = None
            for idx, doc_name in enumerate(retrieved_doc_names):
                if target_doc.lower() in doc_name.lower() or doc_name.lower() in target_doc.lower():
                    target_rank = idx + 1
                    break

            retrieval_hit = target_rank is not None

            if target_rank == 1:
                hits_at_1 += 1
            if target_rank and target_rank <= 3:
                hits_at_3 += 1
            if retrieval_hit:
                hits_at_k += 1
                sum_mrr += (1.0 / target_rank)
                sum_precision += (1.0 / max(1, len(retrieved_doc_names)))
            else:
                sum_mrr += 0.0

            if answer == UNAVAILABLE_INFO_MESSAGE or not retrieval_res.is_confident:
                unanswered_count += 1
                groundedness = 0.0
            else:
                groundedness = self.compute_groundedness(answer, expected_answer)

            sum_groundedness += groundedness

            detailed_results.append(
                EvaluationResultItem(
                    question_id=q_id,
                    question=query,
                    expected_answer=expected_answer,
                    generated_answer=answer,
                    expected_document=target_doc,
                    retrieved_documents=retrieved_doc_names,
                    retrieval_hit=retrieval_hit,
                    retrieval_rank=target_rank,
                    similarity_score=round(retrieval_res.max_score, 4),
                    groundedness_score=round(groundedness, 4),
                    latency_ms=round(elapsed_ms, 2)
                )
            )

        resp = EvaluationBenchmarkResponse(
            total_samples=total_samples,
            recall_at_1=round(hits_at_1 / total_samples, 4),
            recall_at_3=round(hits_at_3 / total_samples, 4),
            recall_at_k=round(hits_at_k / total_samples, 4),
            precision_at_k=round(sum_precision / total_samples, 4),
            mean_reciprocal_rank=round(sum_mrr / total_samples, 4),
            average_groundedness=round(sum_groundedness / total_samples, 4),
            average_latency_ms=round(sum_latency / total_samples, 2),
            unanswered_rate_percent=round((unanswered_count / total_samples) * 100, 2),
            evaluated_at=datetime.now(timezone.utc),
            detailed_results=detailed_results
        )

        # Store in DB if db session provided
        if db:
            try:
                run_record = EvaluationRun(
                    metrics_json=resp.model_dump_json(),
                    total_samples=total_samples
                )
                db.add(run_record)
                db.commit()
            except Exception as e:
                print(f"[EvaluationService] Failed to persist evaluation run: {e}")

        return resp


evaluation_service = EvaluationService()
