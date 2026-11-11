"""
Tests for Vector Database and RAG Retrieval
"""

import pytest
from rag_pipeline import ensure_knowledge_base_initialized, answer_student_query
from config import UNVERIFIED_FALLBACK_MESSAGE


def test_knowledge_base_initialization():
    """Verify that the knowledge base initializes with indexed documents."""
    total_chunks = ensure_knowledge_base_initialized()
    assert total_chunks > 0, "ChromaDB should have indexed chunks"


def test_answer_supported_query():
    """Verify that a supported question retrieves correct sources and provides an answer."""
    ensure_knowledge_base_initialized()
    query = "What is the minimum attendance requirement?"
    result = answer_student_query(query)

    assert result["status"] == "success"
    assert len(result["sources"]) > 0
    # Check that Attendance Regulations is among the sources
    doc_names = [s["document"] for s in result["sources"]]
    assert any("Attendance_Regulations" in d for d in doc_names)
    assert len(result["answer"]) > 20


def test_answer_unsupported_query():
    """Verify that an unsupported query triggers the institutional fallback."""
    ensure_knowledge_base_initialized()
    query = "What is the procedure to book a rocket flight to Mars from campus?"
    result = answer_student_query(query)

    assert result["status"] == "unverified"
    assert len(result["sources"]) == 0
    assert UNVERIFIED_FALLBACK_MESSAGE in result["answer"]
