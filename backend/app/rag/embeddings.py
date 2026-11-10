import os
import numpy as np
from typing import List, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
from app.core.config import settings


class BaseEmbedder:
    def embed_documents(self, texts: List[str]) -> np.ndarray:
        raise NotImplementedError

    def embed_query(self, text: str) -> np.ndarray:
        raise NotImplementedError


class TfidfEmbedder(BaseEmbedder):
    """
    Fast, reliable local TF-IDF vectorizer producing L2-normalized dense embeddings.
    Zero network latency, zero heavy PyTorch dependencies.
    """
    def __init__(self, max_features: int = 1536, model_path: str = None):
        self.max_features = max_features
        self.model_path = model_path or os.path.join(settings.VECTOR_STORE_DIR, "tfidf_model.pkl")
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=self.max_features,
            sublinear_tf=True,
            stop_words="english",
            token_pattern=r"(?u)\b\w+\b"
        )
        self.is_fitted = False
        self.corpus_cache: List[str] = []
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                import pickle
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    self.vectorizer = data["vectorizer"]
                    self.corpus_cache = data.get("corpus", [])
                    self.is_fitted = True
            except Exception as e:
                print(f"[TfidfEmbedder] Error loading model: {e}")

    def _save_model(self):
        try:
            import pickle
            os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
            with open(self.model_path, "wb") as f:
                pickle.dump({
                    "vectorizer": self.vectorizer,
                    "corpus": self.corpus_cache
                }, f)
        except Exception as e:
            print(f"[TfidfEmbedder] Error saving model: {e}")

    def fit(self, texts: List[str]):
        if not texts:
            texts = ["university campus student academic policy examination regulation syllabus"]
        self.corpus_cache = list(texts)
        self.vectorizer.fit(self.corpus_cache)
        self.is_fitted = True
        self._save_model()

    def update_corpus_and_fit(self, texts: List[str]):
        combined = list(set(self.corpus_cache + texts))
        if not combined:
            combined = ["university campus student academic policy examination regulation syllabus"]
        self.corpus_cache = combined
        self.vectorizer.fit(self.corpus_cache)
        self.is_fitted = True
        self._save_model()

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        if not self.is_fitted:
            self.fit(texts)
        sparse_vecs = self.vectorizer.transform(texts)
        dense_vecs = sparse_vecs.toarray().astype(np.float32)
        # L2 normalize so dot product equals cosine similarity
        dense_vecs = normalize(dense_vecs, norm="l2", axis=1)
        return dense_vecs

    def embed_query(self, text: str) -> np.ndarray:
        if not self.is_fitted:
            self.fit([text])
        sparse_vec = self.vectorizer.transform([text])
        dense_vec = sparse_vec.toarray().astype(np.float32)
        dense_vec = normalize(dense_vec, norm="l2", axis=1)
        return dense_vec[0]


class GeminiEmbedder(BaseEmbedder):
    """
    Google Gemini text-embedding-004 embedding client.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[GeminiEmbedder] Failed to initialize genai client: {e}")

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        if not self.client:
            raise RuntimeError("Gemini API key not configured")
        
        vectors = []
        for text in texts:
            res = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            # res.embeddings[0].values
            vectors.append(res.embeddings[0].values)
        
        vec_arr = np.array(vectors, dtype=np.float32)
        return normalize(vec_arr, norm="l2", axis=1)

    def embed_query(self, text: str) -> np.ndarray:
        if not self.client:
            raise RuntimeError("Gemini API key not configured")
        res = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        vec = np.array(res.embeddings[0].values, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec


class EmbeddingService:
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.tfidf_embedder = TfidfEmbedder()
        self.gemini_embedder = None
        if settings.GEMINI_API_KEY:
            try:
                self.gemini_embedder = GeminiEmbedder(settings.GEMINI_API_KEY)
            except Exception:
                pass

    def get_embedder(self) -> BaseEmbedder:
        if self.provider == "gemini" and self.gemini_embedder and self.gemini_embedder.client:
            return self.gemini_embedder
        return self.tfidf_embedder

    def fit_corpus(self, texts: List[str]):
        self.tfidf_embedder.update_corpus_and_fit(texts)

    def embed_documents(self, texts: List[str]) -> np.ndarray:
        embedder = self.get_embedder()
        try:
            return embedder.embed_documents(texts)
        except Exception as e:
            print(f"[EmbeddingService] Primary embedder failed ({e}), falling back to TF-IDF")
            return self.tfidf_embedder.embed_documents(texts)

    def embed_query(self, text: str) -> np.ndarray:
        embedder = self.get_embedder()
        try:
            return embedder.embed_query(text)
        except Exception as e:
            print(f"[EmbeddingService] Primary embedder failed ({e}), falling back to TF-IDF")
            return self.tfidf_embedder.embed_query(text)


embedding_service = EmbeddingService()
