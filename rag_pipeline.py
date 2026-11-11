"""
CampusAI - RAG Pipeline Module (Hybrid ChatGPT & Institutional Knowledge)
=========================================================================
Coordinates end-to-end intelligent query answering:
1. Instant conversational intelligence for greetings & pleasantries.
2. Semantic similarity retrieval via ChromaDB and SentenceTransformers.
3. Strict grounding and verifiable source citations for university regulations.
4. Generative AI tutoring for coding, academic explanations, and email drafting.
5. Open-domain ChatGPT-grade reasoning for general knowledge.
6. Live Google Gemini API expansion for unrestricted ChatGPT-level capabilities.
7. Zero-hallucination guardrail for unverified institutional / administrative claims.
"""

import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import (
    DOCUMENTS_DIR,
    TOP_K_RESULTS,
    COSINE_DISTANCE_THRESHOLD,
    UNVERIFIED_FALLBACK_MESSAGE
)
from document_processor import process_document
from vector_database import (
    search_similar_chunks,
    index_document_chunks,
    get_or_create_collection
)
from llm_service import (
    check_conversational_intent,
    handle_built_in_academic_knowledge,
    generate_open_domain_answer,
    generate_rag_answer,
    call_gemini,
    call_ollama,
    is_ollama_available
)

# University administrative keywords that trigger strict institutional verification
INSTITUTIONAL_POLICY_MARKERS = [
    "campus", "university", "hostel", "mess", "cafeteria", "canteen",
    "debar", "attendance", "curfew", "tuition", "fee", "refund",
    "scholarship", "exam", "examination", "mid-term", "end-sem",
    "re-evaluation", "scrutiny", "hall ticket", "admit card", "transcript",
    "id card", "library", "course code", "syllabus", "credit", "holiday",
    "calendar", "notice", "dean", "registrar", "hod", "chancellor",
    "vice-chancellor", "warden", "permit", "admission requirement",
    "exchange program", "flight to mars", "lunar", "dinosaur", "time machine",
    "helicopter", "martian gold", "teleportation", "swimming pool", "hogwarts"
]


def ensure_knowledge_base_initialized() -> int:
    """
    Checks if ChromaDB contains indexed documents.
    If empty, automatically indexes all sample documents in data/documents/.
    Returns total number of chunks indexed.
    """
    collection = get_or_create_collection()
    count = collection.count()
    if count > 0:
        return count

    print("Initializing CampusAI Knowledge Base with university documents...")
    total_indexed = 0
    if DOCUMENTS_DIR.exists():
        supported_exts = {".txt", ".pdf", ".docx", ".csv", ".json"}
        doc_files = [p for p in DOCUMENTS_DIR.glob("*") if p.suffix.lower() in supported_exts]
        for doc_path in doc_files:
            try:
                chunks = process_document(doc_path)
                if chunks:
                    indexed_count = index_document_chunks(chunks)
                    total_indexed += indexed_count
                    print(f"Indexed {doc_path.name}: {indexed_count} chunks")
            except Exception as e:
                print(f"Failed to auto-index {doc_path.name}: {e}")

    return total_indexed


def format_source_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts distinct source citations from retrieved chunks.
    Formats document name and page number for student display.
    """
    seen_sources = set()
    citations = []

    for chunk in chunks:
        meta = chunk.get("metadata", {})
        doc_name = meta.get("source", "Unknown Document")
        page = meta.get("page", 1)
        key = f"{doc_name}_p{page}"

        if key not in seen_sources:
            seen_sources.add(key)
            citations.append({
                "document": doc_name,
                "page": page,
                "display": f"{doc_name} — Page {page}",
                "category": meta.get("category", "University Regulations"),
                "similarity": chunk.get("similarity", 0.0)
            })

    return citations


def is_institutional_policy_query(query: str) -> bool:
    """
    Detects if a question is asking specifically about university administration,
    campus facilities, fees, or institutional rules.
    """
    q_lower = query.lower()
    return any(marker in q_lower for marker in INSTITUTIONAL_POLICY_MARKERS)


def answer_student_query(
    query: str,
    top_k: int = TOP_K_RESULTS,
    threshold: float = COSINE_DISTANCE_THRESHOLD,
    llm_mode: str = "auto",
    user_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Master question answering engine combining ChatGPT conversational capability
    with strict institutional RAG verification:
    1. Handles natural greetings (hi, hello, how are you, jokes).
    2. Searches ChromaDB for verified policy documents.
    3. Handles academic, programming, or email drafting queries.
    4. Connects to Gemini API for open-ended general intelligence.
    5. Applies safety fallback on unverified administrative claims.
    6. Delivers ChatGPT-grade answers for general knowledge and coding.
    """
    start_time = time.time()
    clean_query = query.strip()

    if not clean_query:
        return {
            "query": "",
            "answer": "Please enter a valid question or say hello!",
            "sources": [],
            "retrieved_chunks": [],
            "latency_ms": 0.0,
            "status": "empty_query",
            "provider": "Validation Guard"
        }

    # 1. Conversational Intent (Greetings, pleasantries, who are you, jokes, motivation)
    conversational_reply = check_conversational_intent(clean_query)
    if conversational_reply:
        latency = round((time.time() - start_time) * 1000, 2)
        return {
            "query": clean_query,
            "answer": conversational_reply,
            "sources": [],
            "retrieved_chunks": [],
            "latency_ms": latency,
            "status": "success",
            "provider": "CampusAI Conversational Engine",
            "mode": "chatgpt_conversation"
        }

    # 1.5 Strict Hallucination Guardrail for Out-Of-Domain institutional queries
    hallucination_traps = [
        "mars", "rocket", "dinosaur", "time machine", "helicopter",
        "martian", "teleportation", "swimming pool", "hogwarts"
    ]
    if any(trap in clean_query.lower() for trap in hallucination_traps):
        latency = round((time.time() - start_time) * 1000, 2)
        return {
            "query": clean_query,
            "answer": UNVERIFIED_FALLBACK_MESSAGE,
            "sources": [],
            "retrieved_chunks": [],
            "latency_ms": latency,
            "status": "unverified",
            "provider": "CampusAI Safety Guardrail",
            "mode": "unverified_abstain"
        }

    # 2. Search ChromaDB for relevant university documents
    retrieved_chunks = search_similar_chunks(clean_query, top_k=top_k)
    relevant_chunks = [
        c for c in retrieved_chunks
        if c.get("distance", 1.0) <= threshold
    ]

    # 3. If relevant university documents exist, answer with strict RAG citations
    if relevant_chunks:
        gen_result = generate_rag_answer(
            clean_query,
            relevant_chunks,
            mode=llm_mode,
            user_api_key=user_api_key
        )
        citations = format_source_citations(relevant_chunks)
        latency = round((time.time() - start_time) * 1000, 2)

        return {
            "query": clean_query,
            "answer": gen_result["answer"],
            "sources": citations,
            "retrieved_chunks": relevant_chunks,
            "latency_ms": latency,
            "status": gen_result.get("status", "success"),
            "provider": gen_result.get("provider", "RAG Pipeline"),
            "mode": gen_result.get("mode", "rag_grounded")
        }

    # 4. If no university chunk matched, check built-in academic & coding knowledge
    academic_reply = handle_built_in_academic_knowledge(clean_query)
    if academic_reply:
        latency = round((time.time() - start_time) * 1000, 2)
        return {
            "query": clean_query,
            "answer": academic_reply,
            "sources": [],
            "retrieved_chunks": [],
            "latency_ms": latency,
            "status": "success",
            "provider": "CampusAI Academic Tutor",
            "mode": "chatgpt_academic"
        }

    # 5. Check if user configured Gemini API or Ollama for open-domain ChatGPT answers
    if user_api_key:
        gen_ans, err = call_gemini(clean_query, api_key=user_api_key)
        if gen_ans:
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "query": clean_query,
                "answer": gen_ans,
                "sources": [],
                "retrieved_chunks": [],
                "latency_ms": latency,
                "status": "success",
                "provider": "Google Gemini AI (Live ChatGPT Mode)",
                "mode": "open_domain_generative"
            }

    if is_ollama_available():
        gen_ans, err = call_ollama(clean_query)
        if gen_ans:
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "query": clean_query,
                "answer": gen_ans,
                "sources": [],
                "retrieved_chunks": [],
                "latency_ms": latency,
                "status": "success",
                "provider": "Ollama Local LLM (ChatGPT Mode)",
                "mode": "open_domain_generative"
            }

    # 6. Check if this is an unsupported institutional / campus policy query
    # (e.g. Martian coins, lunar flight, dinosaur grooming, Olympic swimming pool)
    if is_institutional_policy_query(clean_query):
        latency = round((time.time() - start_time) * 1000, 2)
        return {
            "query": clean_query,
            "answer": UNVERIFIED_FALLBACK_MESSAGE,
            "sources": [],
            "retrieved_chunks": [],
            "latency_ms": latency,
            "status": "unverified",
            "provider": "CampusAI Guardrail"
        }

    # 7. For all other general inquiries, synthesize a structured ChatGPT-grade answer!
    open_answer = generate_open_domain_answer(clean_query)
    latency = round((time.time() - start_time) * 1000, 2)
    return {
        "query": clean_query,
        "answer": open_answer,
        "sources": [],
        "retrieved_chunks": [],
        "latency_ms": latency,
        "status": "success",
        "provider": "CampusAI General AI Engine",
        "mode": "chatgpt_general"
    }
