"""
All tunable settings for the RAG pipeline, in one place.

Magic numbers scattered through retrieval code are hard to explain and harder
to tune. Keeping them here means the chunk size, the fusion constant and the
abstain threshold are visible, named, and obviously deliberate choices.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# The embedding model is already downloaded (Phase 4). Without this,
# sentence-transformers checks Hugging Face's servers for model updates on
# every single run, even against a fully cached model - which is the main
# cause of slow startup on every script that loads the embedder. Must be set
# before sentence_transformers is imported anywhere.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


# --- Paths -----------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent

DOCS_DIR = PROJECT_ROOT / "docs"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
LOGS_DIR = PROJECT_ROOT / "logs"
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"

TRACE_FILE = LOGS_DIR / "trace.jsonl"
COLLECTION_NAME = "northbay_docs"

# logs/ and transcripts/ are git-ignored, so they won't exist on a fresh
# clone. Creating them here avoids a "directory not found" crash later.
for directory in (DOCS_DIR, LOGS_DIR, TRANSCRIPTS_DIR):
    directory.mkdir(exist_ok=True)


# --- LLM providers ---------------------------------------------------------
# Groq is primary; Cerebras takes over on a 429 or 5xx. Both speak the
# OpenAI API shape, so only the base URL, key and model name differ.
#
# Both run the same model - gpt-oss-120b - under slightly different IDs. That
# matters: a failover mid-run swaps the provider without swapping the model,
# so answers stay comparable across a single evaluation run.

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"
CEREBRAS_MODEL = "gpt-oss-120b"

# Reranking and grading need repeatable scores, not creative variety.
LLM_TEMPERATURE = 0


# --- Retrieval tuning ------------------------------------------------------
# These ten values are the actual knobs. Everything above is configuration.

# Small, fast, CPU-only. Downloads once (~90MB) on first run.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunk size is a retrieval-quality tradeoff, not plumbing. Too small and a
# cited chunk no longer supports the claim it's cited for; too large and its
# embedding averages several topics into a vector that matches nothing well.
CHUNK_WORDS = 200
CHUNK_OVERLAP_WORDS = 40

# How many candidates each retriever returns before fusion.
RETRIEVE_TOP_K = 10

# Reciprocal Rank Fusion constant. 60 is the conventional default; it damps
# the gap between rank 1 and rank 2 so neither retriever dominates outright.
RRF_K = 60

# Fused candidates sent to the reranker, and how many survive into the prompt.
RERANK_CANDIDATES = 8
FINAL_CONTEXT_CHUNKS = 4

# If the best rerank score (0-10) falls below this, the pipeline runs the
# corrective loop and, failing that, abstains. Hand-tuned against the eval
# set - see DECISIONS.md D-12.
ABSTAIN_THRESHOLD = 4.0

# Caps on query transformation.
MAX_SUB_QUESTIONS = 3
HISTORY_TURNS = 3

# Note: the corrective loop's retry count is deliberately NOT a setting.
# It is fixed at exactly one retry by design (DECISIONS.md D-14) - making it
# configurable would invite unbounded looping, which is the thing the cap
# exists to prevent.


if __name__ == "__main__":
    print("Config loaded.\n")
    print(f"  Project root : {PROJECT_ROOT}")
    print(f"  Docs folder  : {DOCS_DIR}")
    print(f"  Chroma folder: {CHROMA_DIR}")
    print()
    print(f"  Groq model     : {GROQ_MODEL}")
    print(f"  Cerebras model : {CEREBRAS_MODEL}")
    print()
    print(f"  GROQ_API_KEY     {'found' if GROQ_API_KEY else 'MISSING'}")
    print(f"  CEREBRAS_API_KEY {'found' if CEREBRAS_API_KEY else 'MISSING'}")
    print()
    print(f"  Chunk size {CHUNK_WORDS}w (overlap {CHUNK_OVERLAP_WORDS}w), "
          f"top-{RETRIEVE_TOP_K} per retriever, RRF k={RRF_K}")
    print(f"  Rerank {RERANK_CANDIDATES} candidates -> keep "
          f"{FINAL_CONTEXT_CHUNKS}, abstain below {ABSTAIN_THRESHOLD}/10")
