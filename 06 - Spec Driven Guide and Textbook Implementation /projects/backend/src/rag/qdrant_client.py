"""
Qdrant Vector Database Client
Interactive Textbook - Agentic AI in DevOps
"""

import os
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

# Configuration
COLLECTION_NAME = "textbook_chunks"
VECTOR_SIZE = 384  # MiniLM-L6-v2 embedding dimension


def get_qdrant_client() -> QdrantClient:
    """Get configured Qdrant client."""
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    if not url:
        raise ValueError("QDRANT_URL environment variable is required")

    return QdrantClient(
        url=url,
        api_key=api_key,
    )


async def ensure_collection_exists(client: QdrantClient) -> bool:
    """
    Ensure the textbook_chunks collection exists.
    Creates it if it doesn't exist.

    Returns:
        bool: True if collection exists or was created successfully
    """
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if COLLECTION_NAME not in collection_names:
            # Create collection with vector configuration
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                ),
                # Optimized for small dataset (<200 chunks)
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0,  # Index immediately for small dataset
                ),
            )
            print(f"Created collection: {COLLECTION_NAME}")

        return True

    except Exception as e:
        print(f"Error ensuring collection exists: {e}")
        return False


async def upsert_chunks(
    client: QdrantClient,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
) -> bool:
    """
    Upsert document chunks with embeddings.

    Args:
        client: Qdrant client instance
        chunks: List of chunk metadata dicts with keys:
            - chunk_id: str
            - chapter_slug: str
            - chapter_title: str
            - section_title: str
            - chunk_text: str
            - chunk_index: int
        embeddings: List of embedding vectors (same order as chunks)

    Returns:
        bool: True if successful
    """
    try:
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                models.PointStruct(
                    id=chunk.get("chunk_id", str(i)),
                    vector=embedding,
                    payload={
                        "chapter_slug": chunk.get("chapter_slug"),
                        "chapter_title": chunk.get("chapter_title"),
                        "section_title": chunk.get("section_title"),
                        "chunk_text": chunk.get("chunk_text"),
                        "chunk_index": chunk.get("chunk_index", i),
                    }
                )
            )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(f"Upserted {len(points)} chunks to {COLLECTION_NAME}")
        return True

    except Exception as e:
        print(f"Error upserting chunks: {e}")
        return False


async def search_similar(
    client: QdrantClient,
    query_embedding: List[float],
    limit: int = 3,
    chapter_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search for similar chunks using vector similarity.

    Args:
        client: Qdrant client instance
        query_embedding: Query vector
        limit: Maximum number of results
        chapter_filter: Optional chapter slug to filter results

    Returns:
        List of matching chunks with scores and payloads
    """
    try:
        # Build filter if chapter specified
        query_filter = None
        if chapter_filter:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="chapter_slug",
                        match=models.MatchValue(value=chapter_filter),
                    )
                ]
            )

        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=limit,
            query_filter=query_filter,
        )

        return [
            {
                "score": result.score,
                "chapter_slug": result.payload.get("chapter_slug"),
                "chapter_title": result.payload.get("chapter_title"),
                "section_title": result.payload.get("section_title"),
                "chunk_text": result.payload.get("chunk_text"),
            }
            for result in results
        ]

    except Exception as e:
        print(f"Error searching: {e}")
        return []


async def delete_by_chapter(client: QdrantClient, chapter_slug: str) -> bool:
    """
    Delete all chunks for a specific chapter.

    Args:
        client: Qdrant client instance
        chapter_slug: Chapter slug to delete

    Returns:
        bool: True if successful
    """
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="chapter_slug",
                            match=models.MatchValue(value=chapter_slug),
                        )
                    ]
                )
            )
        )
        print(f"Deleted chunks for chapter: {chapter_slug}")
        return True

    except Exception as e:
        print(f"Error deleting chapter chunks: {e}")
        return False


async def get_collection_stats(client: QdrantClient) -> Dict[str, Any]:
    """
    Get statistics about the collection.

    Returns:
        Dict with collection statistics
    """
    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
        return {
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status.value,
        }
    except Exception as e:
        return {"error": str(e)}


# Health check function
async def check_qdrant_health() -> Dict[str, Any]:
    """
    Check Qdrant connection health.

    Returns:
        Dict with health status
    """
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        return {
            "status": "healthy",
            "collections_count": len(collections.collections),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }