"""
RAG Retriever for Chatbot
Interactive Textbook - Agentic AI in DevOps
"""

import os
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

from .qdrant_client import get_qdrant_client, search_similar

# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_SOURCES = 3  # Maximum sources to retrieve


class Retriever:
    """RAG retriever for textbook content."""

    def __init__(self):
        """Initialize the retriever with embedding model."""
        self.model = None
        self.client = None

    def _get_model(self) -> SentenceTransformer:
        """Lazy-load the embedding model."""
        if self.model is None:
            print(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.model = SentenceTransformer(EMBEDDING_MODEL)
        return self.model

    def _get_client(self):
        """Lazy-load the Qdrant client."""
        if self.client is None:
            self.client = get_qdrant_client()
        return self.client

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query string.

        Args:
            query: User's question

        Returns:
            Embedding vector
        """
        model = self._get_model()
        embedding = model.encode([query], show_progress_bar=False)
        return embedding[0].tolist()

    async def retrieve(
        self,
        query: str,
        max_sources: int = MAX_SOURCES,
        chapter_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User's question
            max_sources: Maximum number of sources to retrieve
            chapter_filter: Optional chapter slug to filter results

        Returns:
            List of relevant chunks with citations
        """
        # Generate embedding for query
        query_embedding = self.embed_query(query)

        # Search Qdrant
        client = self._get_client()
        results = await search_similar(
            client=client,
            query_embedding=query_embedding,
            limit=max_sources,
            chapter_filter=chapter_filter,
        )

        return results

    def format_citations(
        self,
        sources: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """
        Format sources as citations for chatbot response.

        Args:
            sources: Raw source results from retrieval

        Returns:
            Formatted citations
        """
        citations = []
        for source in sources:
            citations.append({
                "chapterSlug": source.get("chapter_slug", ""),
                "sectionTitle": source.get("section_title", ""),
                "chunkText": source.get("chunk_text", "")[:200] + "...",
            })
        return citations


# Global retriever instance
_retriever: Optional[Retriever] = None


def get_retriever() -> Retriever:
    """Get or create the global retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


async def retrieve_for_chat(
    query: str,
    max_sources: int = MAX_SOURCES,
) -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Convenience function to retrieve and format sources for chat.

    Args:
        query: User's question
        max_sources: Maximum number of sources

    Returns:
        Tuple of (raw_sources, formatted_citations)
    """
    retriever = get_retriever()
    sources = await retriever.retrieve(query, max_sources)
    citations = retriever.format_citations(sources)
    return sources, citations