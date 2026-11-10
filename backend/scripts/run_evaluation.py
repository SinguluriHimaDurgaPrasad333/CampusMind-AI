"""
CampusMind AI - Standalone Evaluation Script
Runs the evaluation benchmark over the labelled university dataset
and prints comprehensive retrieval & grounding metrics.
"""
import sys
import os

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.session import init_db, SessionLocal
from app.main import seed_initial_knowledge_base
from app.services.evaluator import evaluation_service


def main():
    print("=" * 70)
    print(" CampusMind AI — Automated RAG Evaluation Benchmark ")
    print("=" * 70)

    # 1. Initialize DB and Seed Knowledge base
    init_db()
    seed_initial_knowledge_base()

    # 2. Run evaluation
    db = SessionLocal()
    try:
        print("\nExecuting evaluation over labelled student questions...")
        res = evaluation_service.run_benchmark(db)

        print("\n--- Benchmark Evaluation Summary ---")
        print(f"Total Benchmark Samples:     {res.total_samples}")
        print(f"Retrieval Recall@1:          {res.recall_at_1 * 100:.1f}%")
        print(f"Retrieval Recall@3:          {res.recall_at_3 * 100:.1f}%")
        print(f"Retrieval Recall@K:          {res.recall_at_k * 100:.1f}%")
        print(f"Retrieval Precision@K:       {res.precision_at_k * 100:.1f}%")
        print(f"Mean Reciprocal Rank (MRR):  {res.mean_reciprocal_rank:.4f}")
        print(f"Average Groundedness Score:  {res.average_groundedness * 100:.1f}%")
        print(f"Average Latency:             {res.average_latency_ms:.1f} ms")
        print(f"Unanswered Query Rate:       {res.unanswered_rate_percent:.1f}%")
        print("=" * 70)

        print("\nSample Detailed Results:")
        for r in res.detailed_results[:5]:
            status_icon = "PASS" if r.retrieval_hit else "FAIL"
            print(f"[{status_icon}] {r.question_id}: {r.question}")
            print(f"       Expected: {r.expected_document} (Hit at Rank: {r.retrieval_rank})")
            print(f"       Answer:   {r.generated_answer[:90]}...")
            print()

    finally:
        db.close()


if __name__ == "__main__":
    main()
