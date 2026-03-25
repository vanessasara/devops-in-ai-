"""
Textbook Content Indexer for RAG
Interactive Textbook - Agentic AI in DevOps

Indexes textbook chapters into Qdrant vector database.
Run once during deployment or when content changes.
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import re

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# Import from backend
from backend.src.rag.qdrant_client import (
    get_qdrant_client,
    ensure_collection_exists,
    upsert_chunks,
    delete_by_chapter,
)

# Configuration
DOCS_PATH = Path(__file__).parent.parent.parent / "website" / "docs"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 64  # tokens


def get_embedding_model() -> SentenceTransformer:
    """Load the sentence transformer model."""
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    return SentenceTransformer(EMBEDDING_MODEL)


def parse_mdx_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse an MDX file and extract content.

    Returns:
        Dict with title, content, and metadata
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"')

            content = parts[2].strip()

    # Extract title from frontmatter or first heading
    title = frontmatter.get('title', '')
    if not title:
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)

    # Extract slug from filename
    slug = file_path.stem

    return {
        "slug": slug,
        "title": title,
        "content": content,
        "frontmatter": frontmatter,
    }


def split_into_sections(content: str) -> List[Dict[str, str]]:
    """
    Split content into sections based on headings.

    Returns:
        List of {title, content} dicts
    """
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    current_content = []

    for line in content.split('\n'):
        if line.startswith('## '):
            # Save previous section
            if current_content:
                current_section["content"] = '\n'.join(current_content).strip()
                sections.append(current_section)

            # Start new section
            current_section = {
                "title": line[3:].strip(),
                "content": ""
            }
            current_content = []
        else:
            current_content.append(line)

    # Add final section
    if current_content:
        current_section["content"] = '\n'.join(current_content).strip()
        sections.append(current_section)

    return sections


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.

    Uses approximate word count as proxy for tokens.
    """
    words = text.split()
    chunks = []

    # Approximate: 1 token ≈ 0.75 words for English
    words_per_chunk = int(chunk_size * 0.75)
    overlap_words = int(overlap * 0.75)

    i = 0
    while i < len(words):
        chunk_words = words[i:i + words_per_chunk]
        if chunk_words:
            chunks.append(' '.join(chunk_words))
        i += words_per_chunk - overlap_words

    return chunks


def generate_chunk_id(chapter_slug: str, section_title: str, chunk_index: int) -> str:
    """Generate a unique ID for a chunk."""
    content = f"{chapter_slug}:{section_title}:{chunk_index}"
    return hashlib.md5(content.encode()).hexdigest()[:16]


def process_chapter(
    chapter: Dict[str, Any],
    model: SentenceTransformer,
) -> tuple[List[Dict[str, Any]], List[List[float]]]:
    """
    Process a chapter into chunks with embeddings.

    Returns:
        Tuple of (chunks, embeddings)
    """
    chunks = []
    texts_to_embed = []

    sections = split_into_sections(chapter["content"])

    for section in sections:
        section_chunks = chunk_text(section["content"])

        for i, chunk_text in enumerate(section_chunks):
            chunk_id = generate_chunk_id(
                chapter["slug"],
                section["title"],
                i
            )

            chunks.append({
                "chunk_id": chunk_id,
                "chapter_slug": chapter["slug"],
                "chapter_title": chapter["title"],
                "section_title": section["title"],
                "chunk_text": chunk_text,
                "chunk_index": i,
            })
            texts_to_embed.append(chunk_text)

    # Generate embeddings
    print(f"  Generating embeddings for {len(texts_to_embed)} chunks...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=False)

    return chunks, embeddings.tolist()


async def index_textbook():
    """Main indexing function."""
    print("=" * 60)
    print("Textbook RAG Indexer")
    print("=" * 60)

    # Initialize
    model = get_embedding_model()
    client = get_qdrant_client()

    # Ensure collection exists
    print("\nEnsuring collection exists...")
    await ensure_collection_exists(client)

    # Find all MDX files
    print(f"\nScanning docs directory: {DOCS_PATH}")
    if not DOCS_PATH.exists():
        print(f"ERROR: Docs path not found: {DOCS_PATH}")
        return False

    mdx_files = list(DOCS_PATH.glob("*.md")) + list(DOCS_PATH.glob("*.mdx"))
    print(f"Found {len(mdx_files)} chapter files")

    # Process each chapter
    all_chunks = []
    all_embeddings = []

    for file_path in sorted(mdx_files):
        print(f"\nProcessing: {file_path.name}")
        chapter = parse_mdx_file(file_path)

        # Delete existing chunks for this chapter
        await delete_by_chapter(client, chapter["slug"])

        # Process chapter
        chunks, embeddings = process_chapter(chapter, model)

        all_chunks.extend(chunks)
        all_embeddings.extend(embeddings)

        print(f"  {len(chunks)} chunks extracted")

    # Upsert all chunks
    print(f"\nUpserting {len(all_chunks)} total chunks...")
    success = await upsert_chunks(client, all_chunks, all_embeddings)

    if success:
        print("\n✅ Indexing complete!")
        return True
    else:
        print("\n❌ Indexing failed!")
        return False


if __name__ == "__main__":
    import asyncio
    asyncio.run(index_textbook())