"""
Hybrid retrieval: BM25 (keyword search) + vector search (semantic search),
fused with Reciprocal Rank Fusion.

BM25 scores and cosine similarities are not on a comparable scale -
BM25 is unbounded and depends on corpus statistics, cosine sits in a compressed
0.3-0.8 band. 
RRF sidesteps this by fusing on rank position only, never on the raw scores themselves.
See DECISIONS.md D-09.
"""

import json

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

import config

# Loaded lazily, once, on first use - not at import time, since the vector
# model and the Chroma collection are only needed once a search actually runs.
_embedder = None
_chroma_collection = None
_bm25 = None
_bm25_chunks = None


def _load_chunks():
    chunks_file = config.CHROMA_DIR / "chunks.json"
    if not chunks_file.exists():
        raise SystemExit(f"No index found at {chunks_file}. Run `python ingest.py` first.")
    with open(chunks_file, encoding="utf-8") as f:
        return json.load(f)


def _get_bm25():
    global _bm25, _bm25_chunks
    if _bm25 is None:
        _bm25_chunks = _load_chunks()
        tokenized = [c["text"].lower().split() for c in _bm25_chunks]
        _bm25 = BM25Okapi(tokenized)
    return _bm25, _bm25_chunks


def _get_chroma_collection():
    global _chroma_collection
    if _chroma_collection is None:
        client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
        _chroma_collection = client.get_collection(config.COLLECTION_NAME)
    return _chroma_collection


def _get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(config.EMBEDDING_MODEL)
    return _embedder


def bm25_search(query, top_k=config.RETRIEVE_TOP_K):
    """Keyword search. Returns chunk dicts, best match first."""
    bm25, chunks = _get_bm25()
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [chunks[i] for i in ranked[:top_k]]


def vector_search(query, top_k=config.RETRIEVE_TOP_K):
    """Semantic search. Returns chunk dicts, best match first."""
    collection = _get_chroma_collection()
    embedder = _get_embedder()
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "chunk_id": results["ids"][0][i],
            "doc_id": results["metadatas"][0][i]["doc_id"],
            "source_file": results["metadatas"][0][i]["source_file"],
            "text": results["documents"][0][i],
        })
    return chunks


def reciprocal_rank_fusion(ranked_lists, k=config.RRF_K):
    """Fuse several ranked chunk lists into one, using rank position only -
    never the raw BM25/cosine scores. See DECISIONS.md D-09."""
    rrf_scores = {}
    chunk_by_id = {}

    for ranked_list in ranked_lists:
        for rank, chunk in enumerate(ranked_list):
            chunk_by_id[chunk["chunk_id"]] = chunk
            rrf_scores.setdefault(chunk["chunk_id"], 0.0)
            rrf_scores[chunk["chunk_id"]] += 1 / (k + rank + 1)

    fused_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)
    return [chunk_by_id[cid] for cid in fused_ids], rrf_scores


def hybrid_search(query, top_k=config.RETRIEVE_TOP_K):
    """Main entry point used by the rest of the pipeline: BM25 + vector
    search, fused with RRF."""
    bm25_results = bm25_search(query, top_k)
    vector_results = vector_search(query, top_k)
    fused, _ = reciprocal_rank_fusion([bm25_results, vector_results])
    return fused


if __name__ == "__main__":
    query = "What version is the Shopify connector on?"
    print(f"Query: {query}\n")
    for chunk in hybrid_search(query, top_k=3):
        print(f"  {chunk['chunk_id']}: {chunk['text'][:80]}...")
