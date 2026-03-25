"""
Embedding Generation Module
Interactive Textbook - Agentic AI in DevOps
"""

import os
from typing import List, Union
from sentence_transformers import SentenceTransformer

# Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # MiniLM-L6-v2 dimension


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformers model
        """
        self.model_name = model_name
        self.model = None

    def _load_model(self) -> SentenceTransformer:
        """Lazy-load the model."""
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def encode(
        self,
        texts: Union[str, List[str]],
        show_progress_bar: bool = False,
    ) -> List[List[float]]:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts
            show_progress_bar: Whether to show progress for batch encoding

        Returns:
            List of embedding vectors
        """
        model = self._load_model()

        # Handle single text
        if isinstance(texts, str):
            texts = [texts]

        # Generate embeddings
        embeddings = model.encode(
            texts,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
        )

        # Convert to list of lists
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: User query

        Returns:
            Embedding vector
        """
        embeddings = self.encode(query)
        return embeddings[0]

    def embed_documents(
        self,
        documents: List[str],
        show_progress_bar: bool = True,
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            documents: List of document texts
            show_progress_bar: Whether to show progress

        Returns:
            List of embedding vectors
        """
        return self.encode(documents, show_progress_bar=show_progress_bar)

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        return EMBEDDING_DIMENSION


# Global instance
_embedding_generator: EmbeddingGenerator = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get or create the global embedding generator instance."""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator