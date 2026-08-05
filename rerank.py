"""
LLM-based reranking: score the fused candidates 0-10 for actual relevance to
the query, in ONE batched call rather than one call per candidate - scoring
them together lets the model rank them relative to each other, instead of
producing eight uncalibrated absolute scores. See DECISIONS.md D-11.
"""

import json

import config
from llm_client import call_llm

SYSTEM_PROMPT = """You score how relevant each candidate passage is to \
answering a query, on a scale of 0 to 10.

0 means the passage has nothing to do with the query. 10 means the passage \
directly and completely contains the information needed to answer it. \
Score based on whether the passage actually contains the answer - not just \
whether it's on a related topic.

Respond with ONLY valid JSON, no other text, no markdown fences:
{"scores": [{"index": 1, "score": 0}, {"index": 2, "score": 0}, ...]}

Include exactly one entry per candidate, using the 1-based index shown, in \
any order."""


def _build_user_prompt(query, candidates):
    lines = [f"Query: {query}", "", "Candidates:"]
    for i, c in enumerate(candidates, start=1):
        lines.append(f"{i}. {c['text']}")
    return "\n".join(lines)


def _parse_scores(text, num_candidates):
    # gpt-oss is a reasoning model and sometimes wraps its answer in
    # markdown fences or a stray sentence of reasoning before the JSON,
    # despite being told not to. Pulling out the {...} substring handles
    # both cases without needing an exact prefix match.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise json.JSONDecodeError("No JSON object found", text, 0)

    parsed = json.loads(text[start:end + 1])
    entries = parsed["scores"]

    scores_by_index = {}
    for entry in entries:
        idx = int(entry["index"])
        scores_by_index[idx] = float(entry["score"])

    # A candidate the model didn't score gets 0, not a guess.
    return [scores_by_index.get(i, 0.0) for i in range(1, num_candidates + 1)]


def rerank_candidates(query, candidates):
    """Takes fused candidates (already RRF-ordered), returns the top
    FINAL_CONTEXT_CHUNKS re-sorted by LLM-judged relevance, each carrying
    its score under "rerank_score".

    On any parse failure, falls back to the existing RRF order with no
    score attached - a broken rerank step should not crash the pipeline,
    it should just skip the reordering.
    """
    pool = candidates[:config.RERANK_CANDIDATES]
    if not pool:
        return []

    user_prompt = _build_user_prompt(query, pool)
    raw = call_llm(SYSTEM_PROMPT, user_prompt, purpose="rerank")

    try:
        scores = _parse_scores(raw, len(pool))
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        for c in pool:
            c["rerank_score"] = None
        return pool[:config.FINAL_CONTEXT_CHUNKS]

    for c, score in zip(pool, scores):
        c["rerank_score"] = score

    ranked = sorted(pool, key=lambda c: c["rerank_score"], reverse=True)
    return ranked[:config.FINAL_CONTEXT_CHUNKS]


if __name__ == "__main__":
    from retrieval import hybrid_search

    def run_test(label, query):
        print("=" * 70)
        print(f"{label}\nQuery: {query}\n")

        candidates = hybrid_search(query)
        ranked = rerank_candidates(query, candidates)

        for c in ranked:
            preview = c["text"][:70].replace("\n", " ")
            print(f"  score={c['rerank_score']}  [{c['doc_id']}] {preview}...")

        top_score = ranked[0]["rerank_score"] if ranked else 0
        print(f"\n  Top score: {top_score}  (abstain threshold: {config.ABSTAIN_THRESHOLD})\n")

    run_test(
        "Test 1: well-covered question (expect a high top score)",
        "What version is the Shopify connector on?",
    )
    run_test(
        "Test 2: deliberate coverage gap (expect a low top score)",
        "What is Northbay's refund policy?",
    )
