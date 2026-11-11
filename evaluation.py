"""
CampusAI - Evaluation Engine Module
===================================
Evaluates RAG performance against the labelled student-question benchmark dataset.
Calculates:
1. Retrieval Hit Rate (Recall@K): % of answerable queries where expected document is retrieved.
2. Semantic Answer Similarity: Cosine similarity between generated answer and ground truth.
3. Average Response Latency: Mean query processing time in milliseconds.
4. Answerability Accuracy: Correct identification of answerable vs unanswerable queries.
5. Category-wise and question-level breakdown.
"""

import time
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from config import EVALUATION_FILE, UNVERIFIED_FALLBACK_MESSAGE
from rag_pipeline import answer_student_query
from vector_database import get_embedding_model


def load_evaluation_dataset() -> pd.DataFrame:
    """Loads the 40+ question labelled benchmark dataset from CSV."""
    if not EVALUATION_FILE.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at {EVALUATION_FILE}")

    df = pd.read_csv(EVALUATION_FILE)
    # Normalize string boolean values
    if "answerable" in df.columns:
        df["answerable"] = df["answerable"].astype(str).str.strip().str.lower().isin(["true", "1", "yes"])
    return df


def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Computes cosine similarity between two text strings using the SentenceTransformer model.
    Returns float score between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0

    model = get_embedding_model()
    embeddings = model.encode([text1, text2], convert_to_numpy=True)
    emb1, emb2 = embeddings[0], embeddings[1]

    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    sim = float(np.dot(emb1, emb2) / (norm1 * norm2))
    return max(0.0, min(1.0, (sim + 1.0) / 2.0))  # Rescaled to 0-1 range


def run_rag_evaluation(
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    limit: Optional[int] = None,
    llm_mode: str = "auto"
) -> Dict[str, Any]:
    """
    Executes benchmark evaluation across all labelled test questions.
    Returns a comprehensive dictionary with KPI metrics, category breakdowns,
    and row-level comparison data.
    """
    df = load_evaluation_dataset()
    if limit and limit > 0:
        df = df.head(limit)

    total_questions = len(df)
    results = []

    retrieval_hits = 0
    answerable_count = 0
    unanswerable_count = 0
    correct_refusals = 0
    similarity_scores = []
    latencies = []

    for idx, row in df.iterrows():
        q_id = str(row.get("question_id", f"Q-{idx+1}"))
        question = str(row.get("question", "")).strip()
        expected_ans = str(row.get("expected_answer", "")).strip()
        expected_src = str(row.get("expected_source", "")).strip().lower()
        category = str(row.get("category", "General")).strip()
        is_answerable = bool(row.get("answerable", True))

        if progress_callback:
            progress_callback(idx + 1, total_questions, f"Evaluating {q_id}: {question[:40]}...")

        # Run query through RAG pipeline
        rag_output = answer_student_query(question, llm_mode=llm_mode)
        actual_ans = rag_output.get("answer", "")
        latency = rag_output.get("latency_ms", 0.0)
        latencies.append(latency)

        retrieved_sources = [s.get("document", "").lower() for s in rag_output.get("sources", [])]

        # Check retrieval hit: was expected document retrieved?
        is_hit = False
        if is_answerable and expected_src and expected_src != "none":
            is_hit = any(expected_src in r_src or r_src in expected_src for r_src in retrieved_sources)
            if is_hit:
                retrieval_hits += 1
            answerable_count += 1
        elif not is_answerable:
            unanswerable_count += 1

        # Check Answerability & Refusal accuracy
        is_refusal = (
            UNVERIFIED_FALLBACK_MESSAGE.lower() in actual_ans.lower()
            or len(rag_output.get("sources", [])) == 0
        )

        if not is_answerable and is_refusal:
            correct_refusals += 1
            sim_score = 1.0  # Perfect handling of unanswerable query
        elif is_answerable and not is_refusal:
            sim_score = calculate_semantic_similarity(actual_ans, expected_ans)
            similarity_scores.append(sim_score)
        elif is_answerable and is_refusal:
            sim_score = 0.0  # Missed supported question
            similarity_scores.append(0.0)
        else:
            # Unanswerable question but gave an answer (false positive)
            sim_score = 0.0

        results.append({
            "question_id": q_id,
            "category": category,
            "question": question,
            "is_answerable": is_answerable,
            "expected_source": row.get("expected_source", "None"),
            "retrieved_sources": ", ".join([s.get("display", "") for s in rag_output.get("sources", [])]) or "None",
            "retrieval_hit": is_hit if is_answerable else "N/A",
            "expected_answer": expected_ans,
            "actual_answer": actual_ans,
            "semantic_similarity": round(sim_score, 4),
            "latency_ms": latency,
            "status": "Correct Refusal" if (not is_answerable and is_refusal) else ("Success" if is_hit else "Mismatch")
        })

    results_df = pd.DataFrame(results)

    # Compute high-level KPI metrics
    hit_rate = (retrieval_hits / answerable_count * 100.0) if answerable_count > 0 else 0.0
    avg_similarity = float(np.mean(similarity_scores) * 100.0) if similarity_scores else 0.0
    refusal_accuracy = (correct_refusals / unanswerable_count * 100.0) if unanswerable_count > 0 else 100.0
    overall_answerability = (
        (retrieval_hits + correct_refusals) / total_questions * 100.0
    ) if total_questions > 0 else 0.0
    avg_latency = float(np.mean(latencies)) if latencies else 0.0

    # Category-wise metrics
    cat_summary = []
    for cat_name, group in results_df.groupby("category"):
        cat_ans = group[group["is_answerable"] == True]
        cat_hits = (cat_ans["retrieval_hit"] == True).sum() if len(cat_ans) > 0 else 0
        cat_hit_rate = (cat_hits / len(cat_ans) * 100.0) if len(cat_ans) > 0 else 100.0
        cat_sim = group["semantic_similarity"].mean() * 100.0
        cat_lat = group["latency_ms"].mean()

        cat_summary.append({
            "Category": cat_name,
            "Questions": len(group),
            "Retrieval Hit Rate (%)": round(cat_hit_rate, 1),
            "Avg Similarity (%)": round(cat_sim, 1),
            "Avg Latency (ms)": round(cat_lat, 1)
        })

    return {
        "summary": {
            "total_questions": total_questions,
            "answerable_questions": answerable_count,
            "unanswerable_questions": unanswerable_count,
            "retrieval_hit_rate": round(hit_rate, 1),
            "average_similarity": round(avg_similarity, 1),
            "refusal_accuracy": round(refusal_accuracy, 1),
            "overall_accuracy": round(overall_answerability, 1),
            "average_latency_ms": round(avg_latency, 1)
        },
        "category_summary": pd.DataFrame(cat_summary),
        "detailed_results": results_df
    }
