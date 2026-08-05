"""
Proves the retrieval-contrast pair works as designed: one query BM25 should
win (exact tokens in doc 05), one query vector search should win (paraphrase
against doc 06's prose). This output is the evidence for the README's
"why hybrid retrieval" section.
"""

from retrieval import bm25_search, vector_search, reciprocal_rank_fusion

CASES = [
    {
        "label": "Exact-token query - BM25 should win",
        "query": "What version is the Shopify connector on?",
        "expected_doc": "05_integration_guide",
    },
    {
        "label": "Paraphrase query - vector search should win",
        "query": "How do you keep track of what the agents are doing?",
        "expected_doc": "06_governance_observability",
    },
]


def show(label, chunks):
    print(f"  {label}:")
    if not chunks:
        print("    (no results)")
        return
    for i, c in enumerate(chunks[:5], 1):
        preview = c["text"][:70].replace("\n", " ")
        print(f"    {i}. [{c['doc_id']}] {preview}...")


def main():
    for case in CASES:
        print("=" * 70)
        print(case["label"])
        print(f'Query: "{case["query"]}"')
        print(f"Expected best match: {case['expected_doc']}")
        print()

        bm25_results = bm25_search(case["query"], top_k=5)
        vector_results = vector_search(case["query"], top_k=5)
        fused, _ = reciprocal_rank_fusion([bm25_results, vector_results])

        show("BM25 (keyword) top 5", bm25_results)
        print()
        show("Vector (semantic) top 5", vector_results)
        print()
        show("RRF fused top 5", fused)
        print()


if __name__ == "__main__":
    main()
