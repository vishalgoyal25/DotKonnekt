"""
Loads docs/, splits into chunks, embeds them, and builds both indexes:
  - ChromaDB (vector search) - persisted to disk, this is the slow step
  - BM25 (keyword search) - rebuilt in memory at retrieval time from the
    chunk text saved here, since BM25Okapi is cheap to construct and
    doesn't need its own persistence format

Run this once before main.py, and again any time docs/ changes.
"""

import json
import re

import chromadb
from sentence_transformers import SentenceTransformer

import config


def load_documents(docs_dir):
    """Read every .md file, stripping the leading synthetic-content comment."""
    docs = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"<!--.*?-->", "", text, count=1, flags=re.DOTALL).strip()
        docs.append({"doc_id": path.stem, "source_file": path.name, "text": text})
    return docs


def chunk_document(doc):
    """Pack paragraphs into ~CHUNK_WORDS-word chunks, never splitting a
    paragraph across two chunks. Each new chunk starts with the last
    CHUNK_OVERLAP_WORDS words of the previous one, so an answer sitting
    right at a chunk boundary isn't lost by both neighbours."""
    paragraphs = [p.strip() for p in doc["text"].split("\n\n") if p.strip()]

    chunks = []
    current = []
    for para in paragraphs:
        para_words = para.split()
        if current and len(current) + len(para_words) > config.CHUNK_WORDS:
            chunks.append(" ".join(current))
            overlap = current[-config.CHUNK_OVERLAP_WORDS:]
            current = overlap + para_words
        else:
            current.extend(para_words)
    if current:
        chunks.append(" ".join(current))

    return chunks


def build_chunk_records(docs):
    records = []
    for doc in docs:
        for i, text in enumerate(chunk_document(doc)):
            records.append({
                "chunk_id": f"{doc['doc_id']}_chunk{i}",
                "doc_id": doc["doc_id"],
                "source_file": doc["source_file"],
                "text": text,
            })
    return records


def store_in_chroma(chunks, embedder):
    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))

    # Re-running ingest.py should replace the index, not stack duplicates
    # on top of it.
    existing = [c.name for c in client.list_collections()]
    if config.COLLECTION_NAME in existing:
        client.delete_collection(config.COLLECTION_NAME)
    collection = client.create_collection(config.COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"doc_id": c["doc_id"], "source_file": c["source_file"]} for c in chunks],
    )


def save_chunks_for_bm25(chunks):
    chunks_file = config.CHROMA_DIR / "chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    return chunks_file


def main():
    print("Loading documents...")
    docs = load_documents(config.DOCS_DIR)
    if not docs:
        raise SystemExit(f"No documents found in {config.DOCS_DIR}. Nothing to ingest.")
    print(f"  {len(docs)} documents loaded")

    print("Chunking...")
    chunks = build_chunk_records(docs)
    print(f"  {len(chunks)} chunks created")

    print(f"Loading embedding model ({config.EMBEDDING_MODEL})...")
    print("  First run downloads ~90MB; cached after that.")
    embedder = SentenceTransformer(config.EMBEDDING_MODEL)

    print("Embedding chunks and writing to ChromaDB...")
    store_in_chroma(chunks, embedder)

    chunks_file = save_chunks_for_bm25(chunks)

    print("\nDone.")
    print(f"  {len(docs)} documents -> {len(chunks)} chunks")
    print(f"  Vector index: {config.CHROMA_DIR}")
    print(f"  Chunk data for BM25: {chunks_file}")


if __name__ == "__main__":
    main()
