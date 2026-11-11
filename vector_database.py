"""
CampusAI - Vector Database Module (ChromaDB + SentenceTransformers)
===================================================================
Manages document embedding generation and persistent vector storage using ChromaDB.
Employs sentence-transformers/all-MiniLM-L6-v2 for semantic vector representations.
Implements file-hash deduplication, document deletion, and similarity search.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Enforce offline mode for Hugging Face Hub & Transformers
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import CHROMA_DIR, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL_NAME

# Global in-memory caches to prevent redundant reloads and multi-client conflicts
_EMBEDDING_MODEL_INSTANCE: Optional[SentenceTransformer] = None
_CHROMA_CLIENT_INSTANCE: Optional[chromadb.PersistentClient] = None
_COLLECTION_INSTANCE: Optional[Any] = None


def get_embedding_model() -> SentenceTransformer:
    """
    Returns the cached SentenceTransformer model instance.
    Loads all-MiniLM-L6-v2 into memory on first call.
    """
    global _EMBEDDING_MODEL_INSTANCE
    if _EMBEDDING_MODEL_INSTANCE is None:
        print(f"Loading SentenceTransformer embedding model: {EMBEDDING_MODEL_NAME}...")
        _EMBEDDING_MODEL_INSTANCE = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _EMBEDDING_MODEL_INSTANCE


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Initializes and returns a cached persistent ChromaDB client pointing to CHROMA_DIR.
    Uses singleton pattern to prevent Rust bindings conflicts in multi-threaded Streamlit.
    """
    global _CHROMA_CLIENT_INSTANCE
    if _CHROMA_CLIENT_INSTANCE is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            _CHROMA_CLIENT_INSTANCE = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
        except Exception:
            try:
                from chromadb.api.shared_system_client import SharedSystemClient
                SharedSystemClient.clear_system_cache()
            except Exception:
                pass
            _CHROMA_CLIENT_INSTANCE = chromadb.PersistentClient(
                path=str(CHROMA_DIR),
                settings=Settings(anonymized_telemetry=False, allow_reset=True)
            )
    return _CHROMA_CLIENT_INSTANCE


def get_or_create_collection(client: Optional[chromadb.PersistentClient] = None):
    """
    Retrieves or creates the ChromaDB collection for CampusAI knowledge base.
    Uses cosine distance metric ('cosine') and caches collection reference.
    """
    global _COLLECTION_INSTANCE, _CHROMA_CLIENT_INSTANCE
    if _COLLECTION_INSTANCE is not None and client is None:
        return _COLLECTION_INSTANCE

    cli = client or get_chroma_client()
    try:
        _COLLECTION_INSTANCE = cli.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception:
        try:
            from chromadb.api.shared_system_client import SharedSystemClient
            SharedSystemClient.clear_system_cache()
        except Exception:
            pass
        _CHROMA_CLIENT_INSTANCE = None
        cli = get_chroma_client()
        _COLLECTION_INSTANCE = cli.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _COLLECTION_INSTANCE


def is_document_indexed(filename: str, file_hash: str) -> bool:
    """
    Checks if a document with the same filename and hash is already indexed.
    Prevents duplicate chunks in ChromaDB.
    """
    collection = get_or_create_collection()
    results = collection.get(
        where={"file_hash": file_hash},
        limit=1
    )
    return len(results.get("ids", [])) > 0


def delete_document_by_filename(filename: str) -> int:
    """
    Deletes all vector chunks belonging to a specific filename from ChromaDB.
    Returns the number of chunks deleted.
    """
    collection = get_or_create_collection()
    existing = collection.get(where={"source": filename})
    ids_to_delete = existing.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)
    return 0


def index_document_chunks(chunks: List[Dict[str, Any]]) -> int:
    """
    Encodes text chunks using SentenceTransformers and adds them to ChromaDB.
    Safely deletes old chunks of the document if an updated version is uploaded.
    """
    if not chunks:
        return 0

    collection = get_or_create_collection()
    model = get_embedding_model()

    # Identify document filename and remove any preexisting version
    sample_meta = chunks[0]["metadata"]
    filename = sample_meta.get("source", "")
    if filename:
        delete_document_by_filename(filename)

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Generate dense vector embeddings (384-dimensional for all-MiniLM-L6-v2)
    embeddings = model.encode(texts, convert_to_numpy=True).tolist()

    # Add to ChromaDB
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_similar_chunks(
    query: str,
    top_k: int = 4
) -> List[Dict[str, Any]]:
    """
    Executes semantic vector search for a student query:
    1. Generates question embedding using SentenceTransformer.
    2. Queries ChromaDB for top_k nearest neighbors.
    3. Converts cosine distance to normalized similarity score (1 - distance).
    4. Returns sorted list of matching chunk dictionaries.
    """
    clean_query = query.strip()
    if not clean_query:
        return []

    collection = get_or_create_collection()
    total_chunks = collection.count()
    if total_chunks == 0:
        return []

    model = get_embedding_model()
    query_embedding = model.encode([clean_query], convert_to_numpy=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, total_chunks),
        include=["documents", "metadatas", "distances"]
    )

    matched_chunks = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        chunk_ids = results["ids"][0] if "ids" in results else [""] * len(docs)

        for text, meta, dist, cid in zip(docs, metas, distances, chunk_ids):
            # ChromaDB cosine distance range: [0, 2]
            # Convert to similarity: 1.0 - distance
            similarity = max(0.0, 1.0 - float(dist))
            matched_chunks.append({
                "chunk_id": cid,
                "text": text,
                "metadata": meta,
                "distance": float(dist),
                "similarity": similarity
            })

    # Sort descending by similarity
    matched_chunks.sort(key=lambda x: x["similarity"], reverse=True)
    return matched_chunks


def get_indexed_documents_stats() -> List[Dict[str, Any]]:
    """
    Aggregates metadata of all documents currently indexed in ChromaDB.
    Returns list of distinct documents with chunk counts, category, and date.
    """
    collection = get_or_create_collection()
    all_items = collection.get(include=["metadatas"])

    metadatas = all_items.get("metadatas", [])
    doc_map: Dict[str, Dict[str, Any]] = {}

    for meta in metadatas:
        source = meta.get("source", "Unknown")
        category = meta.get("category", "General")
        upload_date = meta.get("upload_timestamp", "N/A")

        if source not in doc_map:
            doc_map[source] = {
                "filename": source,
                "category": category,
                "upload_date": upload_date,
                "chunks_count": 0,
                "status": "Indexed"
            }
        doc_map[source]["chunks_count"] += 1

    return list(doc_map.values())


def reset_collection() -> None:
    """Clears and recreates the ChromaDB collection."""
    client = get_chroma_client()
    try:
        client.delete_collection(name=CHROMA_COLLECTION_NAME)
    except Exception:
        pass
    get_or_create_collection(client)
