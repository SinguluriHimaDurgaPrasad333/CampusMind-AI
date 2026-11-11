"""
Pre-indexes university documents into the memory-safe vector store.
"""
from rag_pipeline import ensure_knowledge_base_initialized

if __name__ == "__main__":
    print("Pre-indexing university documents for fast deployment...", flush=True)
    count = ensure_knowledge_base_initialized()
    print(f"Successfully indexed {count} document chunks into vector store!", flush=True)
