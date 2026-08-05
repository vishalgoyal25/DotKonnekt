"""
Corrective retrieval: if the top rerank score is too weak, ask the LLM to
reformulate the query once, re-run retrieval + rerank, and keep whichever
attempt actually scored better. Capped at exactly one retry - no
open-ended looping. See DECISIONS.md D-14.
"""

import config
from llm_client import call_llm
from retrieval import bm25_search, vector_search, reciprocal_rank_fusion
from rerank import rerank_candidates

REFORMULATE_SYSTEM_PROMPT = """The following question returned weak search \
results from a document corpus. Rewrite it as a single alternative search \
query that might retrieve better matches - try a different angle: broader \
if the original was too narrow, or more specific if it was too generic.

Respond with ONLY the rewritten query text - no quotes, no explanation."""


def maybe_retry(query, first_attempt_chunks):
    """first_attempt_chunks: already-reranked list from the first pass.

    Returns (final_chunks, retried, reformulated_query) - all three are
    returned even when the retry didn't help, so the caller can record
    exactly what happened for this turn (inspectable state, Phase 10).
    """
    top_score = (first_attempt_chunks[0].get("rerank_score") or 0) if first_attempt_chunks else 0

    if top_score >= config.ABSTAIN_THRESHOLD:
        return first_attempt_chunks, False, None

    reformulated = call_llm(REFORMULATE_SYSTEM_PROMPT, query, purpose="corrective").strip()

    ranked_lists = [bm25_search(reformulated), vector_search(reformulated)]
    fused, _ = reciprocal_rank_fusion(ranked_lists)
    retry_chunks = rerank_candidates(reformulated, fused)

    retry_score = (retry_chunks[0].get("rerank_score") or 0) if retry_chunks else 0

    # A "corrective" step that blindly overwrites can make things worse -
    # keep whichever attempt actually scored better. DECISIONS.md D-14.
    if retry_score > top_score:
        return retry_chunks, True, reformulated
    return first_attempt_chunks, True, reformulated
