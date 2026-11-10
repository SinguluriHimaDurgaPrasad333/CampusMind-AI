import re
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store, ChunkMetadata
from app.schemas.chat import CitationItem

STOP_QUERY_WORDS = {
    "what", "is", "are", "the", "a", "an", "in", "of", "to", "for", "with", "without",
    "how", "can", "do", "does", "explain", "describe", "define", "tell", "me", "about",
    "student", "students", "campus", "university", "college", "institute"
}


class RetrievalResult:
    def __init__(
        self,
        chunks: List[ChunkMetadata],
        citations: List[CitationItem],
        max_score: float,
        is_confident: bool
    ):
        self.chunks = chunks
        self.citations = citations
        self.max_score = max_score
        self.is_confident = is_confident


class Retriever:
    def __init__(
        self,
        similarity_threshold: float = None,
        top_k: int = None
    ):
        self.similarity_threshold = similarity_threshold or settings.SIMILARITY_THRESHOLD
        self.top_k = top_k or settings.TOP_K_RETRIEVAL

    def retrieve(self, query: str) -> RetrievalResult:
        """
        Embeds the query and retrieves the top-k relevant document chunks with hybrid keyword boosting.
        """
        if not query or not query.strip():
            return RetrievalResult([], [], 0.0, False)

        # 1. Extract significant query content keywords
        query_words = [w.lower() for w in re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", query) if w.lower() not in STOP_QUERY_WORDS]

        # 2. Embed query and run vector search
        query_vec = embedding_service.embed_query(query)
        search_results: List[Tuple[ChunkMetadata, float]] = vector_store.similarity_search(
            query_vec, top_k=self.top_k * 3  # fetch larger candidate pool for re-ranking
        )

        if not search_results:
            return RetrievalResult([], [], 0.0, False)

        # 3. Hybrid re-ranking: boost chunks containing exact query keywords (acronyms like DHCP, DNS, etc.)
        reranked_results = []
        for chunk_meta, score in search_results:
            boosted_score = score
            content_lower = chunk_meta.content.lower()

            # Exact keyword matches
            matched_keywords = 0
            for kw in query_words:
                if re.search(r"\b" + re.escape(kw) + r"\b", content_lower):
                    matched_keywords += 1

            if query_words:
                match_ratio = matched_keywords / len(query_words)
                if match_ratio > 0:
                    boosted_score += (match_ratio * 0.35)

            reranked_results.append((chunk_meta, boosted_score, matched_keywords))

        # Sort descending by boosted score
        reranked_results.sort(key=lambda x: x[1], reverse=True)
        top_candidates = reranked_results[:self.top_k]

        max_score = top_candidates[0][1] if top_candidates else 0.0
        
        # If the query had significant content terms, ensure adequate topical grounding
        is_confident = max_score >= self.similarity_threshold
        if query_words and top_candidates[0][2] == 0:
            is_confident = False
        elif len(query_words) >= 3 and top_candidates[0][2] < 2 and max_score < 0.22:
            is_confident = False

        chunks: List[ChunkMetadata] = []
        citations: List[CitationItem] = []

        for chunk_meta, score, matches in top_candidates:
            if score >= self.similarity_threshold:
                chunks.append(chunk_meta)
                snippet = chunk_meta.content[:240].strip() + ("..." if len(chunk_meta.content) > 240 else "")
                citations.append(
                    CitationItem(
                        document_name=chunk_meta.document_name,
                        category=chunk_meta.category,
                        page_number=chunk_meta.page_number,
                        score=round(float(score), 4),
                        snippet=snippet
                    )
                )

        return RetrievalResult(
            chunks=chunks,
            citations=citations,
            max_score=float(max_score),
            is_confident=is_confident
        )


retriever = Retriever()
