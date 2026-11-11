"""
Tests for Evaluation Benchmark Module
"""

import pytest
import pandas as pd
from evaluation import load_evaluation_dataset, calculate_semantic_similarity, run_rag_evaluation


def test_load_evaluation_dataset():
    """Verify that evaluation questions dataset contains at least 40 questions."""
    df = load_evaluation_dataset()
    assert len(df) >= 40, f"Expected at least 40 questions, got {len(df)}"
    assert "question" in df.columns
    assert "expected_source" in df.columns
    assert "expected_answer" in df.columns
    assert "category" in df.columns
    assert "answerable" in df.columns


def test_semantic_similarity_identical():
    """Identical sentences should have high semantic similarity (~1.0)."""
    text = "The attendance requirement is 75% for writing semester exams."
    sim = calculate_semantic_similarity(text, text)
    assert sim >= 0.95


def test_semantic_similarity_different():
    """Completely unrelated sentences should have much lower similarity."""
    text1 = "Students must attend 75% of classes to write exams."
    text2 = "Astronauts eat freeze-dried ice cream on the International Space Station."
    sim = calculate_semantic_similarity(text1, text2)
    assert sim < 0.70


def test_evaluation_small_batch():
    """Run a small sample evaluation to verify KPI computation."""
    res = run_rag_evaluation(limit=5)
    assert "summary" in res
    assert "category_summary" in res
    assert "detailed_results" in res
    summary = res["summary"]
    assert summary["total_questions"] == 5
    assert summary["retrieval_hit_rate"] >= 0.0
