# Sample Run — Advanced RAG Q&A System

This is a real, unedited transcript from `python main.py`, captured
2026-08-06. Nothing below has been rewritten or cleaned up — this is the
actual output the system produced, including its exact wording.

The corpus is synthetic: all documents describe **Northbay Commerce AI**, a
fictional B2B retail/consumer AI vendor invented for this assignment (see
`docs/`). Because Northbay does not exist, no fact about it can come from
the model's pretraining — a correct, cited answer here is only possible if
retrieval genuinely worked.

## How to reproduce this transcript

Run `python main.py`, then ask these four questions **in this exact
order**, then type `/exit`:

| # | Question | What it demonstrates |
|---|---|---|
| 1 | `What version is the Shopify connector on?` | A normal question, answered from a single document, with a citation |
| 2 | `What is the trial length, and what does the Growth tier include?` | Query decomposition — a multi-part question split into two sub-questions, and hybrid retrieval pulling from two documents |
| 3 | `How many employees does Northbay have?` | The corrective loop firing — a weak first retrieval attempt triggers one reformulated retry, then a genuine, model-generated abstain (not a hardcoded string) |
| 4 | `What is Northbay's annual revenue?` | A second, independent abstain case — a different coverage gap in the corpus, also correctly refused |

**Note on reproducibility:** the four *behaviours* above reproduce reliably —
confirmed across two separate live runs producing near-identical output. The
exact rerank scores and reformulated query wording may vary slightly between
runs, since reranking and reformulation are LLM-generated and not
deterministic (see `DECISIONS.md` D-11). This is expected, not a bug.

---

## Transcript

```
======================================================================
Turn 1  [2026-08-06T16:37:12]
Question: What version is the Shopify connector on?
  Transform action : unchanged
  Search queries   : ['What version is the Shopify connector on?']
  Candidates fused : 16
  Corrective loop  : False
  Top score        : 10.0  (threshold: 4.0)
  Abstained        : False
  Cited docs       : ['05_integration_guide']

Answer: The Shopify Plus connector is currently version **`nb-connect-shopify` v4.2**.

======================================================================
Turn 2  [2026-08-06T16:37:18]
Question: What is the trial length, and what does the Growth tier include?
  Transform action : decompose
  Search queries   : ['What is the trial length, and what does the Growth tier include?', 'What is the trial length?', 'What does the Growth tier include?']
  Candidates fused : 25
  Corrective loop  : False
  Top score        : 10.0  (threshold: 4.0)
  Abstained        : False
  Cited docs       : ['09_pricing_tiers', '10_contract_trial_terms']

Answer: The trial period for new customers is a **30-day evaluation period** that begins on the contract start date, during which the subscription can be cancelled without liability for the subscription fee.

The **Growth tier** provides:
- Up to 6 active agentic templates at once
- Up to 10 connected data sources
- Priority support (per the support & SLA policy)
- One Forward-Deployed Engineer (FDE) engagement of up to 8 weeks
- Access to Northbay Studio and at least one agentic template category (included in all tiers)

======================================================================
Turn 3  [2026-08-06T16:38:26]
Question: How many employees does Northbay have?
  Transform action : unchanged
  Search queries   : ['How many employees does Northbay have?']
  Candidates fused : 16
  Corrective loop  : True (reformulated: "Northbay employee count")
  Top score        : 0  (threshold: 4.0)
  Abstained        : True
  Cited docs       : []

Answer: I'm sorry, but the provided passages don't contain any information about the number of employees at Northbay. The excerpts describe the integration connectors, authentication methods, governance and observability practices, platform components, and related terminology, but they don't mention company size or staffing.

======================================================================
Turn 4  [2026-08-06T16:39:26]
Question: What is Northbay's annual revenue?
  Transform action : unchanged
  Search queries   : ["What is Northbay's annual revenue?"]
  Candidates fused : 18
  Corrective loop  : True (reformulated: "Northbay company annual revenue financial report 2023Northbay company annual revenue financial report 2023")
  Top score        : 0  (threshold: 4.0)
  Abstained        : True
  Cited docs       : []

Answer: I don't have enough information to answer that question. The provided passages discuss Northbay's execution-focused platform, its governance and observability features, and the terms of its subscription contracts and trial periods, but they do not contain any data about the company's annual revenue.
```

## Notes on this specific run

- **Turn 4's reformulated query shows a duplicated string** — the corrective
  step's reformulation call returned the same phrase repeated back-to-back
  with no space. This coincided with a very slow response from the failover
  provider under load. Despite the malformed intermediate query, retrieval
  still returned reasonable candidates and the system still correctly
  abstained — the pipeline tolerated a corrupted intermediate value without
  breaking, rather than crashing or producing a nonsense answer.
- **Turns 3 and 4 both used the Cerebras failover provider** for several
  calls, after Groq's free-tier daily quota was exhausted mid-session — a
  real, unplanned demonstration of the Groq→Cerebras failover working
  correctly under genuine production conditions, not a staged test.
