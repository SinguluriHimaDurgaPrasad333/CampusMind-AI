import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from app.core.config import settings

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class ChunkMetadata:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        document_name: str,
        category: str,
        page_number: int,
        chunk_index: int,
        content: str
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_name = document_name
        self.category = category
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "category": self.category,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "content": self.content
        }


class VectorStore:
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or settings.VECTOR_STORE_DIR
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index_path = os.path.join(self.storage_dir, "campusmind.faiss")
        self.meta_path = os.path.join(self.storage_dir, "campusmind_meta.pkl")

        self.faiss_index = None
        self.metadata_store: List[ChunkMetadata] = []
        self.vector_store_matrix: Optional[np.ndarray] = None
        self.dimension: Optional[int] = None

        # Load existing index if available
        self.load()

    def _init_faiss(self, dim: int):
        self.dimension = dim
        if HAS_FAISS:
            # IndexFlatIP computes inner product (cosine similarity for normalized vectors)
            self.faiss_index = faiss.IndexFlatIP(dim)
        else:
            self.faiss_index = None

    def add_chunks(
        self,
        embeddings: np.ndarray,
        metadatas: List[ChunkMetadata]
    ):
        """Add embedding vectors and their associated metadata."""
        if embeddings is None or len(embeddings) == 0:
            return

        dim = embeddings.shape[1]
        if self.dimension is None or self.dimension != dim:
            self._init_faiss(dim)
            self.vector_store_matrix = embeddings
        else:
            if self.vector_store_matrix is None or len(self.vector_store_matrix) == 0:
                self.vector_store_matrix = embeddings
            else:
                self.vector_store_matrix = np.vstack([self.vector_store_matrix, embeddings])

        if HAS_FAISS and self.faiss_index is not None:
            self.faiss_index.add(embeddings.astype(np.float32))

        self.metadata_store.extend(metadatas)
        self.save()

    def similarity_search(
        self,
        query_vector: np.ndarray,
        top_k: int = None
    ) -> List[Tuple[ChunkMetadata, float]]:
        """
        Search for top_k most similar chunks.
        Returns list of (ChunkMetadata, similarity_score).
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL
        if len(self.metadata_store) == 0 or self.vector_store_matrix is None:
            return []

        actual_k = min(top_k, len(self.metadata_store))
        query_arr = np.array([query_vector], dtype=np.float32)

        # 1. FAISS Search
        if HAS_FAISS and self.faiss_index is not None and self.faiss_index.ntotal > 0:
            scores, indices = self.faiss_index.search(query_arr, actual_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if 0 <= idx < len(self.metadata_store):
                    results.append((self.metadata_store[idx], float(score)))
            return results

        # 2. Exact NumPy Cosine Similarity Fallback
        scores = np.dot(self.vector_store_matrix, query_vector)
        top_indices = np.argsort(scores)[::-1][:actual_k]
        results = []
        for idx in top_indices:
            results.append((self.metadata_store[idx], float(scores[idx])))
        return results

    def delete_document(self, document_id: str):
        """Remove all chunks belonging to a document and rebuild index."""
        if not self.metadata_store:
            return

        remaining_indices = [
            i for i, meta in enumerate(self.metadata_store)
            if meta.document_id != document_id
        ]

        if len(remaining_indices) == len(self.metadata_store):
            return  # Document not found in vector store

        if remaining_indices and self.vector_store_matrix is not None:
            self.metadata_store = [self.metadata_store[i] for i in remaining_indices]
            self.vector_store_matrix = self.vector_store_matrix[remaining_indices]
            if HAS_FAISS and self.dimension:
                self.faiss_index = faiss.IndexFlatIP(self.dimension)
                self.faiss_index.add(self.vector_store_matrix.astype(np.float32))
        else:
            self.metadata_store = []
            self.vector_store_matrix = None
            self.faiss_index = None

        self.save()

    def clear(self):
        """Wipe vector index and metadata."""
        self.metadata_store = []
        self.vector_store_matrix = None
        self.faiss_index = None
        self.dimension = None
        if os.path.exists(self.index_path):
            try:
                os.remove(self.index_path)
            except Exception:
                pass
        if os.path.exists(self.meta_path):
            try:
                os.remove(self.meta_path)
            except Exception:
                pass

    def save(self):
        """Persist FAISS index and metadata to disk."""
        try:
            with open(self.meta_path, "wb") as f:
                pickle.dump({
                    "metadata": self.metadata_store,
                    "vectors": self.vector_store_matrix,
                    "dimension": self.dimension
                }, f)

            if HAS_FAISS and self.faiss_index is not None:
                faiss.write_index(self.faiss_index, self.index_path)
        except Exception as e:
            print(f"[VectorStore] Error saving index: {e}")

    def load(self):
        """Load FAISS index and metadata from disk."""
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "rb") as f:
                    data = pickle.load(f)
                    self.metadata_store = data.get("metadata", [])
                    self.vector_store_matrix = data.get("vectors")
                    self.dimension = data.get("dimension")

                if HAS_FAISS and os.path.exists(self.index_path):
                    self.faiss_index = faiss.read_index(self.index_path)
                elif HAS_FAISS and self.vector_store_matrix is not None and self.dimension:
                    self.faiss_index = faiss.IndexFlatIP(self.dimension)
                    self.faiss_index.add(self.vector_store_matrix.astype(np.float32))
            except Exception as e:
                print(f"[VectorStore] Error loading index: {e}")


vector_store = VectorStore()
