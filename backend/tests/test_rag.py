import os
import pytest
import numpy as np
from app.rag.document_processor import DocumentProcessor
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore, ChunkMetadata
from app.rag.retriever import Retriever
from app.rag.llm import LLMService, UNAVAILABLE_INFO_MESSAGE


def test_document_processor_chunking():
    processor = DocumentProcessor(chunk_size=200, chunk_overlap=40)
    sample_text = (
        "Regulations Governing Student Attendance.\n\n"
        "1. Minimum Attendance Requirement: Every registered student must secure a minimum attendance of 75% in aggregate across all lectures.\n\n"
        "2. Medical Condonation: Up to 10% condonation may be granted in genuine medical emergencies."
    )
    pages = [(sample_text, 1)]
    chunks = processor.chunk_text(pages)
    
    assert len(chunks) >= 2
    assert chunks[0].page_number == 1
    assert "75%" in chunks[0].content or "75%" in chunks[1].content


def test_embedding_and_vector_store(tmp_path):
    storage_dir = str(tmp_path / "vstore")
    vstore = VectorStore(storage_dir=storage_dir)
    embedder = EmbeddingService()
    embedder.tfidf_embedder.model_path = str(tmp_path / "test_tfidf.pkl")

    texts = [
        "The minimum attendance requirement is 75 percent for semester exams.",
        "Hostel curfew time is 10:00 PM on weekdays and 10:30 PM on weekends.",
        "Undergraduate students can borrow 4 books from the campus library."
    ]
    embedder.fit_corpus(texts)
    vectors = embedder.embed_documents(texts)

    metas = [
        ChunkMetadata("c1", "d1", "Attendance.txt", "Attendance", 1, 0, texts[0]),
        ChunkMetadata("c2", "d2", "Hostel.txt", "Hostel", 1, 0, texts[1]),
        ChunkMetadata("c3", "d3", "Library.txt", "Admin", 1, 0, texts[2]),
    ]

    vstore.add_chunks(vectors, metas)
    assert len(vstore.metadata_store) == 3

    # Query for curfew
    query_vec = embedder.embed_query("What time do I need to be back in the hostel?")
    results = vstore.similarity_search(query_vec, top_k=1)
    assert len(results) == 1
    top_meta, score = results[0]
    assert top_meta.document_id == "d2"
    assert "curfew" in top_meta.content.lower()


def test_llm_grounding_and_disclaimer():
    llm = LLMService()
    # Test unavailable query
    answer, is_grounded = llm.generate_answer(
        query="Can students keep a pet giraffe in the dorms?",
        chunks=[],
        citations=[],
        is_confident=False
    )
    assert answer == UNAVAILABLE_INFO_MESSAGE
    assert is_grounded is False
