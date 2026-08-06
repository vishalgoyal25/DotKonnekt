"""
Wires query transformation, hybrid retrieval, reranking, the corrective
loop, and grounded generation into one end-to-end pipeline. This is the
first point where all five Track C techniques run together as one system
rather than as five separately-tested parts.

Returns not just the final answer but every intermediate decision - which
query variants were searched, whether the corrective loop fired, the final
score - so a turn is inspectable, not a black box (CLAUDE.md Constraint 1).
"""

from query_transform import transform_query
from retrieval import bm25_search, vector_search, reciprocal_rank_fusion
from rerank import rerank_candidates
from corrective import maybe_retry
from generate import generate_answer


def _search_queries(question, transform_result):
    # Retrieve on the original AND the transformed query/queries - a bad
    # rewrite then degrades results instead of destroying them, since the
    # original is always still in the pool. DECISIONS.md D-10.
    seen = []
    for q in [question] + transform_result["queries"]:
        if q not in seen:
            seen.append(q)
    return seen


def _canonical_query(question, transform_result):
    # The query used for rerank scoring and for the final answer. A
    # rewrite replaces an ambiguous original; a decomposition still answers
    # the original compound question, using context gathered from all its
    # sub-questions.
    if transform_result["action"] == "rewrite":
        return transform_result["queries"][0]
    return question


def answer_question(question, history=None):
    transform_result = transform_query(question, history)
    canonical_query = _canonical_query(question, transform_result)
    search_queries = _search_queries(question, transform_result)

    ranked_lists = []
    for q in search_queries:
        ranked_lists.append(bm25_search(q))
        ranked_lists.append(vector_search(q))
    fused, _ = reciprocal_rank_fusion(ranked_lists)

    # Never call the reranker with an empty candidate list - go straight
    # to the corrective/abstain path instead. DECISIONS.md D-16.
    # (rerank_candidates also guards this internally since Phase 7, so
    # this is belt-and-suspenders, not the only safeguard.)
    ranked = rerank_candidates(canonical_query, fused) if fused else []

    final_chunks, corrective_fired, reformulated_query = maybe_retry(canonical_query, ranked)

    result = generate_answer(canonical_query, final_chunks)

    # Per-source detail for the UI (Phase 11) - purely additive, no new
    # calls. final_chunks already carries doc_id/text/rerank_score per
    # chunk from the rerank step; this just exposes it instead of
    # discarding it down to cited_docs/top_score alone.
    sources = [
        {"doc_id": c["doc_id"], "score": c.get("rerank_score"), "excerpt": c["text"][:300]}
        for c in final_chunks
    ]

    return {
        "question": question,
        "transform_action": transform_result["action"],
        "search_queries": search_queries,
        "canonical_query": canonical_query,
        "num_candidates_fused": len(fused),
        "corrective_fired": corrective_fired,
        "reformulated_query": reformulated_query,
        "sources": sources,
        "top_score": result["top_score"],
        "abstained": result["abstained"],
        "answer": result["answer"],
        "cited_docs": result["cited_docs"],
        "invalid_citations": result["invalid_citations"],
    }


if __name__ == "__main__":
    def run(label, question):
        print("=" * 70)
        print(f"{label}\nQuestion: {question}\n")
        r = answer_question(question)
        print(f"  Transform action: {r['transform_action']}")
        print(f"  Search queries: {r['search_queries']}")
        print(f"  Candidates fused: {r['num_candidates_fused']}")
        fired_note = f' (reformulated: "{r["reformulated_query"]}")' if r["reformulated_query"] else ""
        print(f"  Corrective loop fired: {r['corrective_fired']}{fired_note}")
        print(f"  Top score: {r['top_score']}  Abstained: {r['abstained']}")
        print(f"  Cited: {r['cited_docs']}  Invalid citations: {r['invalid_citations']}")
        print(f"\n  {r['answer']}\n")

    run("Test 1: normal question - no corrective loop expected",
        "What version is the Shopify connector on?")

    run("Test 2: multi-part question - decomposition visible in search_queries",
        "What is the trial length, and what does the Growth tier include?")

    run("Test 3: borderline question - corrective loop SHOULD fire",
        "What is Northbay's refund policy?")

    run("Test 4: genuine coverage gap - should abstain even after the retry",
        "How many employees does Northbay have?")
